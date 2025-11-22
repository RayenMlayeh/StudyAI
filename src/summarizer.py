from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough


class CourseSummarizer:    
    def __init__(self, api_key: str, model: str = "x-ai/grok-4.1-fast"):
        self.llm = ChatOpenAI(
            model=model,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.1,  # Very low temperature to prevent hallucination
            max_tokens=8000
        )
    
    def detect_global_topic(self, documents: List[Document]) -> str:
        # Sample first chunk and a few random chunks to get the gist
        sample_docs = [documents[0]]
        if len(documents) > 5:
            import random
            sample_docs.extend(random.sample(documents[1:], min(3, len(documents)-1)))
            
        context = "\n\n".join([doc.page_content[:1000] for doc in sample_docs])
        
        prompt = f"""Analyze the following course material samples and identify the SINGLE global main topic.
        
        Material Samples:
        {context}
        
        Return ONLY the topic name (e.g., "Cybersecurity", "Linear Algebra", "Marketing Principles").
        Do not add any other text.
        
        Global Topic:"""
        
        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception:
            return "Course Material"

    def generate_summary(self, documents: List[Document], batch_size: int = 20) -> str:
        if not documents:
            return "No documents provided for summarization"
        
        # Detect global topic first
        print("Detecting global topic...")
        global_topic = self.detect_global_topic(documents)
        print(f"Global Topic Detected: {global_topic}")
        
        # Calculate total content length
        full_text = "\n\n".join([doc.page_content for doc in documents])
        total_chars = len(full_text)
        
        # STRATEGY SELECTION
        # If document is small/medium (< 80,000 chars approx 20k tokens), use SINGLE PASS
        # This is better for coherence and global context
        if total_chars < 80000:
            print(f"\n{'='*80}")
            print(f"SINGLE PASS MODE: Processing {total_chars} chars (fits in context)")
            print(f"{'='*80}")
            
            single_pass_prompt = ChatPromptTemplate.from_template(
                f"""Create a CONCISE EXECUTIVE SUMMARY / CHEAT SHEET for the course topic: {{global_topic}}.

STRICT RULES:
1. Analyze the FULL TEXT provided below
2. Synthesize a study guide FOCUSED on: {{global_topic}}
3. IGNORE information unrelated to {{global_topic}}
4. Write EVERYTHING in the SAME LANGUAGE as the text
5. DO NOT add external knowledge

Target: ~1500 words (concise, high-impact cheat sheet)

STRUCTURE YOUR CHEAT SHEET EXACTLY LIKE THIS:

# COURSE TITLE: {{global_topic}}
[One clear title line]

---

# KEY DEFINITIONS

List ONLY the most critical terms:
- Term: Concise definition
[Include only essential vocabulary]

---

# ESSENTIAL FORMULAS

For EACH critical formula:
Formula Name:
- Formula: [Write the actual mathematical expression]
- Variables: [Briefly explain symbols]
- Usage: [When to use (1 line)]

[List only the most important formulas]

---

# MAJOR CONCEPTS

For each core concept:
Concept Name:
- Concise explanation
- Key points

---

# MAIN METHODS

For each key method:
Method Name:
1. Step 1
2. Step 2
[Brief step-by-step]

---

# TYPICAL EXAMPLE

Example:
- Problem: [Problem statement]
- Solution: [Solution steps]
- Answer: [Result]

[Include only 1-2 representative examples]

---

# KEY TAKEAWAYS

- Key point 1
- Key point 2
- Mistake to avoid

COURSE MATERIAL:
{{context}}

Concise Exam Cheat Sheet:""")
            
            chain = single_pass_prompt | self.llm
            response = chain.invoke({"context": full_text, "global_topic": global_topic})
            
            word_count = len(response.content.split())
            print(f"\nStudy guide generated successfully (~{word_count} words)")
            return response.content

        # FALLBACK: MAP-REDUCE FOR LARGE DOCUMENTS (> 80k chars)
        print(f"\n{'='*80}")
        print(f"MAP-REDUCE MODE: Processing {total_chars} chars (too large for single pass)")
        print(f"{'='*80}")

        # Calculate target word counts based on document volume
        num_docs = len(documents)
        if num_docs <= 30:
            batch_words = 300
            final_words = 1000
        elif num_docs <= 50:
            batch_words = 400
            final_words = 1500
        else:
            batch_words = 500
            final_words = 2000
        
        # MAP PHASE: Extract information from each batch
        map_prompt = ChatPromptTemplate.from_template(
            f"""You are analyzing course material chunks. Extract ONLY the MOST CRITICAL study information related to the GLOBAL TOPIC: {{global_topic}}.

STRICT RULES:
1. FOCUS STRICTLY on the Global Topic: {{global_topic}}
2. IGNORE information unrelated to {{global_topic}} (e.g., unrelated examples, tangents)
3. ONLY extract information EXPLICITLY written in the text below
4. DO NOT use any external knowledge
5. Quote the actual subject/topic names from the text

IMPORTANT: Detect the language of the text and respond in the EXACT SAME LANGUAGE.

Extract and list in detail (ONLY if present in text and relevant to {{global_topic}}):

1. KEY DEFINITIONS: Only the most important technical terms
2. ESSENTIAL FORMULAS: Critical mathematical formulas only
3. MAIN METHODS: Key procedures/algorithms
4. MAJOR CONCEPTS: Core theories with brief explanations
5. KEY EXAMPLE: One best example if available

VALIDATION CHECK: Re-read the text below and verify every sentence you write comes DIRECTLY from it and relates to {{global_topic}}.

Target: ~{batch_words} words (concise extraction)

COURSE MATERIAL TO ANALYZE:
{{context}}

My extraction (strictly from above text only):""")
        
        # MAP PHASE: Extract information from each batch
        batch_summaries = []
        total_batches = (len(documents) + batch_size - 1) // batch_size
        
        print(f"\n{'='*80}")
        print(f"MAP PHASE: Processing {len(documents)} documents in {total_batches} batches")
        print(f"{'='*80}")
        
        # Prepare batches
        batch_contexts = []
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            # Create context for this batch
            context_parts = []
            for doc in batch:
                source = doc.metadata.get('source_file', 'Unknown')
                page = doc.metadata.get('page', '?')
                context_parts.append(f"[Source: {source}, Page: {page}]\n{doc.page_content}")
            context = "\n\n---\n\n".join(context_parts)
            batch_contexts.append({"context": context, "global_topic": global_topic})

        # Process batches in parallel
        print(f"Processing {len(batch_contexts)} batches in parallel...")
        chain = map_prompt | self.llm
        
        # Use batch processing with concurrency
        responses = chain.batch(batch_contexts, config={"max_concurrency": 5})
        
        for i, response in enumerate(responses, 1):
            batch_summaries.append(response.content)
            print(f"Processed Batch {i}/{total_batches}")
        
        # REDUCE PHASE: Combine into final study guide
        reduce_prompt = ChatPromptTemplate.from_template(
            f"""Create a CONCISE EXECUTIVE SUMMARY / CHEAT SHEET for the course topic: {{global_topic}}.

ANTI-HALLUCINATION RULES:
1. ONLY use information from the batch extractions below
2. DO NOT add external knowledge
3. Synthesize a study guide FOCUSED on: {{global_topic}}
4. Write EVERYTHING in the SAME LANGUAGE as the batch extractions

Target: ~{final_words} words (concise, high-impact cheat sheet)

STRUCTURE YOUR CHEAT SHEET EXACTLY LIKE THIS:

# COURSE TITLE: {{global_topic}}
[One clear title line]

---

# KEY DEFINITIONS

List ONLY the most critical terms:
- Term: Concise definition
[Include only essential vocabulary]

---

# ESSENTIAL FORMULAS

For EACH critical formula:
Formula Name:
- Formula: [Write the actual mathematical expression]
- Variables: [Briefly explain symbols]
- Usage: [When to use (1 line)]

[List only the most important formulas]

---

# MAJOR CONCEPTS

For each core concept:
Concept Name:
- Concise explanation
- Key points

---

# MAIN METHODS

For each key method:
Method Name:
1. Step 1
2. Step 2
[Brief step-by-step]

---

# TYPICAL EXAMPLE

Example:
- Problem: [Problem statement]
- Solution: [Solution steps]
- Answer: [Result]

[Include only 1-2 representative examples]

---

# KEY TAKEAWAYS

- Key point 1
- Key point 2
- Mistake to avoid

CRITICAL INSTRUCTIONS:
- Focus on QUALITY over QUANTITY.
- Synthesize and condense information.
- Do NOT list every single detail, only what is needed for an exam cheat sheet.
- Keep descriptions brief and to the point.

{{summaries}}

Concise Exam Cheat Sheet:""")
        
        combined_summaries = "\n\n=== BATCH EXTRACTION ===\n\n".join(batch_summaries)
        
        print(f"\n{'='*80}")
        print(f"REDUCE PHASE: Combining {len(batch_summaries)} batch extractions")
        print(f"{'='*80}")
        
        chain = {"summaries": RunnablePassthrough(), "global_topic": RunnablePassthrough()} | reduce_prompt | self.llm
        final_summary = chain.invoke({"summaries": combined_summaries, "global_topic": global_topic})
        
        word_count = len(final_summary.content.split())
        print(f"\nStudy guide generated successfully (~{word_count} words)")
        
        return final_summary.content
    
    def generate_quick_summary(self, context: str, max_length: int = 500) -> str:
        """
        Generate a quick summary of given context
        
        Args:
            context: Text to summarize
            max_length: Maximum words for summary
            
        Returns:
            Brief summary text
        """
        prompt = f"""Provide a concise summary of the following text in approximately {max_length} words.
Focus on the main points and key takeaways.

Text:
{context}

Summary:
"""
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
            
        except Exception as e:
            return f"Error generating summary: {str(e)}"
