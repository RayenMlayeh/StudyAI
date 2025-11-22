"""
Summarizer Module
Generates comprehensive exam study guides using map-reduce strategy
"""

from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough


class CourseSummarizer:
    """Generate comprehensive study guides from course material using map-reduce"""
    
    def __init__(self, api_key: str, model: str = "x-ai/grok-4.1-fast"):
        self.llm = ChatOpenAI(
            model=model,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.1,  # Very low temperature to prevent hallucination
            max_tokens=8000
        )
    
    def generate_summary(self, documents: List[Document], batch_size: int = 10) -> str:
        """
        Generate a comprehensive exam study guide using map-reduce summarization.
        
        This is a token-efficient approach that:
        1. Splits documents into batches (MAP phase)
        2. Extracts key information from each batch
        3. Combines into a final comprehensive study guide (REDUCE phase)
        
        The study guide includes:
        - All definitions, formulas, and concepts
        - Detailed methods and algorithms
        - Worked examples
        - Exam preparation tips
        
        Automatically detects language and responds in the same language (French/English).
        
        Args:
            documents: List of Document objects containing course content
            batch_size: Number of documents per batch
        
        Returns:
            Comprehensive study guide in markdown format
        """
        if not documents:
            return "⚠️ No documents provided for summarization"
        
        # Calculate target word counts based on document volume
        num_docs = len(documents)
        if num_docs <= 10:
            batch_words = 200
            final_words = 500
        elif num_docs <= 30:
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
            f"""You are analyzing course material chunks. Extract ONLY the MOST CRITICAL study information from the provided text below.

**⛔ ABSOLUTE RULES - VIOLATION WILL INVALIDATE YOUR RESPONSE:**
1. ONLY extract information EXPLICITLY written in the text below
2. DO NOT use any external knowledge, memory, or previous training
3. DO NOT invent examples, formulas, or concepts not in this text
4. DO NOT mention topics that don't appear in this specific text
5. If something is not in the text, DO NOT include it
6. Quote the actual subject/topic names from the text (e.g., if text is about "Security", don't mention "Algebra")

**IMPORTANT: Detect the language of the text and respond in the EXACT SAME LANGUAGE (French → French, English → English)**

**FIRST: Identify the main topic/subject from the text (e.g., "Security", "Algebra", "Biology", etc.)**
**Main Topic of this text:** [Write the topic you see in the text]

Extract and list in detail (ONLY if present in text):

1. **DÉFINITIONS CLÉS / KEY DEFINITIONS**: Only the most important technical terms (copy from text)
2. **FORMULES ESSENTIELLES / ESSENTIAL FORMULAS**: Critical mathematical formulas only (copy exactly as shown)
3. **MÉTHODES PRINCIPALES / MAIN METHODS**: Key procedures/algorithms (copy steps from text)
4. **CONCEPTS MAJEURS / MAJOR CONCEPTS**: Core theories with brief explanations (copy from text)
5. **EXEMPLE CLÉ / KEY EXAMPLE**: One best example if available (copy from text)

**VALIDATION CHECK**: Re-read the text below and verify every sentence you write comes DIRECTLY from it.

Target: ~{batch_words} words (concise extraction)

COURSE MATERIAL TO ANALYZE:
{{context}}

My extraction (strictly from above text only):""")
        
        # MAP PHASE: Extract information from each batch
        batch_summaries = []
        total_batches = (len(documents) + batch_size - 1) // batch_size
        
        print(f"\n{'='*80}")
        print(f"📊 MAP PHASE: Processing {len(documents)} documents in {total_batches} batches")
        print(f"{'='*80}")
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            # Create context for this batch - combine chunks without truncation
            context_parts = []
            for doc in batch:
                source = doc.metadata.get('source_file', 'Unknown')
                page = doc.metadata.get('page', '?')
                # Don't truncate - chunks are already sized appropriately
                context_parts.append(f"[Source: {source}, Page: {page}]\n{doc.page_content}")
            context = "\n\n---\n\n".join(context_parts)
            
            # Extract information from batch
            chain = {"context": RunnablePassthrough()} | map_prompt | self.llm
            response = chain.invoke(context)
            batch_summaries.append(response.content)
            
            print(f"  ✓ Batch {batch_num}/{total_batches} processed ({len(batch)} documents)")
        
        # REDUCE PHASE: Combine into final study guide
        reduce_prompt = ChatPromptTemplate.from_template(
            f"""Create a CONCISE EXECUTIVE SUMMARY / CHEAT SHEET by synthesizing the batch extractions below.

**⛔ CRITICAL ANTI-HALLUCINATION RULES:**
1. ONLY use information from the batch extractions below
2. DO NOT add external knowledge or topics not in the extractions
3. Combine ALL topics found in the extractions (e.g., if batches cover "Algebra" AND "Security", include BOTH)
4. Write EVERYTHING in the SAME LANGUAGE as the batch extractions (if mixed, use the dominant language or separate sections)

Target: ~{final_words} words (concise, high-impact cheat sheet)

**STRUCTURE YOUR CHEAT SHEET EXACTLY LIKE THIS:**

#  TITRE DU COURS / COURSE TITLE
[One clear title line]

---

# 📖 DÉFINITIONS CLÉS / KEY DEFINITIONS

List ONLY the most critical terms:
- **Terme/Term**: Définition concise / Concise definition
[Include only essential vocabulary]

---

# 🔢 FORMULES ESSENTIELLES / ESSENTIAL FORMULAS

For EACH critical formula:
**Nom de la formule / Formula name:**
- Formule: [Write the actual mathematical expression]
- Variables: [Briefly explain symbols]
- Utilisation: [When to use (1 line)]

[List only the most important formulas]

---

# 💡 CONCEPTS MAJEURS / MAJOR CONCEPTS

For each core concept:
**Nom du concept / Concept name:**
- Explication concise / Concise explanation
- Points clés / Key points

---

# ⚙️ MÉTHODES PRINCIPALES / MAIN METHODS

For each key method:
**Nom de la méthode / Method name:**
1. Étape 1 / Step 1
2. Étape 2 / Step 2
[Brief step-by-step]

---

# 📝 EXEMPLE TYPE / TYPICAL EXAMPLE

**Exemple / Example:**
- Énoncé / Problem: [Problem statement]
- Solution: [Solution steps]
- Réponse / Answer: [Result]

[Include only 1-2 representative examples]

---

# ⚠️ À RETENIR / KEY TAKEAWAYS

- ✓ Point clé 1 / Key point 1
- ✓ Point clé 2 / Key point 2
- ⚠️ Erreur à éviter / Mistake to avoid

**CRITICAL INSTRUCTIONS:**
- Focus on QUALITY over QUANTITY.
- Synthesize and condense information.
- Do NOT list every single detail, only what is needed for an exam cheat sheet.
- Keep descriptions brief and to the point.

{{summaries}}

Concise Exam Cheat Sheet:""")
        
        combined_summaries = "\n\n=== BATCH EXTRACTION ===\n\n".join(batch_summaries)
        
        print(f"\n{'='*80}")
        print(f"🔄 REDUCE PHASE: Combining {len(batch_summaries)} batch extractions")
        print(f"{'='*80}")
        
        chain = {"summaries": RunnablePassthrough()} | reduce_prompt | self.llm
        final_summary = chain.invoke(combined_summaries)
        
        word_count = len(final_summary.content.split())
        print(f"\n✓ Study guide generated successfully (~{word_count} words)")
        
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
