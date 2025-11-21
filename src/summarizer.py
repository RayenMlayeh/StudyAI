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
            temperature=0.2,
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
            batch_words = 500
            final_words = 2000
        elif num_docs <= 30:
            batch_words = 700
            final_words = 4000
        elif num_docs <= 50:
            batch_words = 900
            final_words = 6000
        else:
            batch_words = 1200
            final_words = 8000
        
        # MAP PHASE: Extract information from each batch
        map_prompt = ChatPromptTemplate.from_template(
            f"""You are analyzing course material chunks. Extract ALL study-relevant information ONLY from the provided text below.

**CRITICAL: Only extract information that is EXPLICITLY present in the text. DO NOT add external knowledge or examples.**

**IMPORTANT: Respond in the SAME LANGUAGE as the course content (French → French, English → English)**

Extract and list in detail:

1. **DÉFINITIONS / DEFINITIONS**: Every technical term with complete definition (from the text)
2. **FORMULES / FORMULAS**: ALL mathematical formulas, equations with:
   - Complete notation (write the actual formula as shown)
   - Variable explanations (if present in text)
   - Numerical examples (only if provided in text)
3. **MÉTHODES / METHODS**: Step-by-step procedures for each algorithm/method (as described in text)
4. **CONCEPTS**: Key theories with explanations (from the text)
5. **EXEMPLES / EXAMPLES**: Worked problems with solutions (only from text)
6. **PROPRIÉTÉS / PROPERTIES**: Important characteristics and rules (from the text)

**DO NOT**: Invent examples, add external knowledge, or discuss topics not in the provided text.

Target: ~{batch_words} words - BE VERY DETAILED about what IS in the text!

COURSE MATERIAL:
{{{{context}}}}

Detailed extraction (only from above text):""")
        
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
            f"""Create a COMPREHENSIVE EXAM CHEAT SHEET from these batch extractions.

**CRITICAL: Write EVERYTHING in the SAME LANGUAGE as the batch extractions below.**

Target: ~{final_words} words (very detailed exam reference)

**STRUCTURE YOUR CHEAT SHEET EXACTLY LIKE THIS:**

# � TITRE DU COURS / COURSE TITLE
[One clear title line]

---

# 📖 DÉFINITIONS CLÉS / KEY DEFINITIONS

List EVERY term as:
- **Terme/Term**: Définition complète / Complete definition
- **Terme/Term**: Définition complète / Complete definition
[Include ALL technical vocabulary]

---

# 🔢 FORMULES MATHÉMATIQUES / MATHEMATICAL FORMULAS

For EACH formula:
**Nom de la formule / Formula name:**
- Formule: [Write the actual mathematical expression]
- Variables: [Explain each symbol]
- Utilisation: [When/how to use]
- Exemple: [Numerical example if available]

[List ALL formulas from the materials - do NOT skip any!]

---

# 💡 CONCEPTS THÉORIQUES / THEORETICAL CONCEPTS

For each concept:
**Nom du concept / Concept name:**
- Explication détaillée / Detailed explanation
- Propriétés clés / Key properties
- Relations avec autres concepts / Relations to other concepts
- Applications / Applications

---

# ⚙️ MÉTHODES ET ALGORITHMES / METHODS & ALGORITHMS

For each method:
**Nom de la méthode / Method name:**
1. Étape 1 / Step 1
2. Étape 2 / Step 2
[Complete step-by-step procedure]
- Entrée/Input: [What goes in]
- Sortie/Output: [What comes out]
- Exemple: [Concrete example]

---

# 📝 EXEMPLES RÉSOLUS / WORKED EXAMPLES

**Exemple 1 / Example 1:**
- Énoncé / Problem: [Full problem statement]
- Solution: [Complete step-by-step solution]
- Réponse finale / Final answer: [Result]

[Include multiple examples for complex topics]

---

# ⚖️ COMPARAISONS / COMPARISONS

| Concept A | vs | Concept B |
|-----------|-----|-----------|
| Différence 1 | | Différence 1 |
| Avantages / Advantages | | Avantages / Advantages |
| Quand utiliser / When to use | | Quand utiliser / When to use |

---

# ⚠️ POINTS IMPORTANTS À RETENIR / KEY POINTS TO REMEMBER

- ✓ Fait critique 1 / Critical fact 1
- ✓ Fait critique 2 / Critical fact 2
- ⚠️ Erreur courante à éviter / Common mistake to avoid
- 💡 Astuce d'examen / Exam tip

---

# 📋 QUESTIONS TYPES D'EXAMEN / TYPICAL EXAM QUESTIONS

**Questions théoriques / Theoretical questions:**
1. [Example question type]
2. [Example question type]

**Exercices de calcul / Calculation problems:**
1. [Example problem type]
2. [Example problem type]

**CRITICAL INSTRUCTIONS:**
- Extract EVERY SINGLE formula from batch summaries (write the actual mathematical expression)
- Include EVERY definition mentioned
- Provide COMPLETE step-by-step methods
- Add worked examples with full solutions
- DO NOT summarize or compress - students need ALL details for exam
- Use bullet points, numbered lists, and tables for easy reference

{{{{summaries}}}}

Complete Exam Cheat Sheet:""")
        
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
