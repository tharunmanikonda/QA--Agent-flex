# Voice Agent QA Analysis and Model Comparison (September 2025)

## Background and objectives

Nike’s customer‑service voice agent answers queries about orders, returns, products and membership.  The current metric—whether a call was handled automatically or escalated to a human—doesn’t tell us whether the interaction truly succeeded.  We need richer quality‑assurance (QA) insights to understand when the voice agent helps customers, partially helps them or fails altogether.  This project demonstrates a prompt‑based QA system that analyses call transcripts and recommends improvements.  It also compares state‑of‑the‑art language models to identify which is most suitable for the task.

## QA analysis design

### Categorisation scheme

Calls are classified into four outcome categories:

| Category | Definition |
|---|---|
| **Automated – Successful** | The call is handled entirely by the AI and the customer’s issue is resolved. |
| **Automated – Partially Successful** | The AI handles the call but the customer still has unresolved concerns. |
| **Escalated – Partially Successful** | The AI provides some useful information before escalating to a human or another channel. |
| **Escalated – Unsuccessful** | The AI fails to help and immediately hands off the call or no human agent is available. |

The analysis also detects the customer’s **intent** (order status, return status, return/refund issue, product question, membership question, etc.).

### Prompt engineering

Three prompts drive the analysis:

1. **Summary prompt:** instructs the model to summarise the transcript in concise bullet points.  It explicitly asks for the customer’s intent, the agent’s actions, the outcome and any miscommunications.
2. **Classification prompt:** provides definitions for the outcome categories and asks the model to choose the appropriate one based on the summary.  The model must return a JSON object with the intent, outcome category and rationale.
3. **Improvement prompt:** uses the summary and classification to generate two to three concrete suggestions for improving similar calls.

These prompts are defined in `prompts.py` and can be tuned without modifying the analysis code.

### System architecture

The core logic lives in `qa_agent.py`.  The function `analyze_transcript` orchestrates the analysis by:

1. **Summarising** the call using the summary prompt.
2. **Classifying** the outcome using the classification prompt and parsing the returned JSON.
3. **Suggesting improvements** using the improvement prompt.

By default the system uses OpenAI’s ChatCompletion API via the `openai` package.  If no API key is configured, a **heuristic fallback** runs instead.  The heuristic implementation uses keyword matching to detect intent, escalation and success and outputs simple canned suggestions.  This fallback enables offline demonstration and unit testing.

Sample transcripts are stored in `sample_transcripts/`.  Running `python run_example.py` analyses these calls and prints a report.  Below is an example of the heuristic output for one call:

```
Call ID: call1
  Intent: Order status
  Outcome: Automated – Successful
  Rationale: Detected intent as 'Order status'. The call was handled entirely by the AI, without escalation. The customer signalled satisfaction and ended the call.
  Summary:
    Intent: Order status
    The AI agent greeted the customer and attempted to assist.
    The call outcome was determined using pattern matching.
  Improvement suggestions:
    Continue confirming the customer's details and summarising the resolution before ending the call.
```

## Model comparison

The QA system relies on a general‑purpose language model to summarise and classify calls.  The choice of model affects cost, accuracy, speed and reliability.  The table below compares several leading models as of September 2025.  Cost figures are taken from public pricing pages (prices per one million tokens).  Performance observations come from benchmark reports and industry analyses.

| Model | Context window & strengths | Cost (input / output) | Notable findings |
|---|---|---|---|
| **OpenAI GPT‑5 / GPT‑4.5 / GPT‑4o** | GPT‑4.5 combines strong logic, multilingual support and fast outputs【286035193800581†L377-L385】; GPT‑5, released August 2025, provides a 128 k token context window and improved multimodal support【286035193800581†L533-L550】.  OpenAI models excel at general creativity and broad ecosystem integration but still produce occasional factual errors【286035193800581†L424-L452】. | GPT‑4o mini: $0.15 / $0.60 M tokens; GPT‑4o: $2.50 / $10【286035193800581†L502-L526】; GPT‑4.5 preview: $75 / $150; GPT‑5 mini/nano on the OpenAI pricing page list input costs of $0.05–$1.25 per million tokens and output costs of $0.40–$10 per million tokens【168110470487445†screenshot】. | Versatile and widely supported; high‑end models are expensive and computationally intensive; prone to occasional hallucinations【286035193800581†L442-L453】. |
| **Anthropic Claude 4 (Opus 4 / Sonnet 4)** | Claude models emphasise safety and long‑context reasoning.  Opus and Sonnet consistently outperform GPT‑4.5 on advanced reasoning benchmarks such as SWE‑Bench and GPQA【286035193800581†L383-L387】.  Claude’s context window reaches 200 k tokens, enabling thorough document analysis【286035193800581†L466-L468】. | Claude 4 Opus: $15 / $75 M tokens; Claude 4 Sonnet: $3 / $15【286035193800581†L502-L527】. | Strong at coding and deep reasoning【286035193800581†L476-L480】 with robust safety mechanisms【286035193800581†L460-L474】; ecosystem smaller than OpenAI and features like “Paprika Mode” are still maturing【286035193800581†L484-L490】. |
| **Meta Llama 4 (Scout / Maverick)** | Llama 4 models use mixture‑of‑experts and native multimodality.  Scout offers an industry‑leading 10 M token context window【683397607396387†L21-L27】 and fits on a single GPU.  Maverick performs comparably to GPT‑4o and Gemini 2.0 Flash at a fraction of the cost【683397607396387†L28-L40】 and scores 73.4 % on MMMU vs. GPT‑4o’s 69.1 %【814009394535977†L130-L151】. | Open‑source versions are free to run on self‑hosted hardware; API providers charge roughly $0.24 per million input tokens and $0.85 per million output tokens according to independent analyses (Meta claims Maverick’s price–performance ratio is 9–23× better than GPT‑4o【814009394535977†L350-L367】). | Open‑weight models allow on‑prem deployment and customization; high context length is ideal for long calls.  However, these models may require more engineering effort to achieve chat‑assistant quality. |
| **Alibaba Qwen‑3 Max** | Qwen‑3‑Max preview has 1 T parameters and supports a 262 k token context window【178232108033890†L69-L71】.  Benchmarks show it leading across reasoning and coding tasks【178232108033890†L40-L43】. | Tiered pricing: $0.861 / $3.441 M tokens (0–32 k input), $1.434 / $5.735 M (32–128 k), $2.151 / $8.602 M (128–252 k)【178232108033890†L80-L91】. | Early tests report very fast responses and strong reasoning abilities【178232108033890†L60-L75】, but the model is not open‑source and currently available only via paid APIs. |
| **Mistral AI (7B / Mixtral 8×7B / Mistral Large)** | Mistral offers open‑source and commercial models.  Mixtral 8×7B outperforms Llama 2 70B and matches or exceeds GPT‑3.5 on many benchmarks【230138646397761†L81-L88】.  Mistral Large is a powerful commercial model comparable to GPT‑4【230138646397761†L218-L227】.  Open models have context windows around 32 k tokens. | Pay‑as‑you‑go pricing: Mistral 7B costs $0.25 / $0.25 M tokens; Mixtral 8×7B: $0.70 / $0.70; Mixtral 8×22B: $2 / $6; Mistral Small: $1 / $3; Mistral Large: $4 / $12【230138646397761†L175-L189】. | Open‑source models are inexpensive and easily self‑hosted; Mixtral models offer strong performance at low cost.  Commercial models provide higher accuracy but still cost less than GPT‑4【230138646397761†L234-L238】. |
| **Google Gemini 2.5 Pro / Flash** | Gemini models are fully multimodal across text, image, video and audio.  Gemini 2.5 Flash has a 1 M token context window and costs $0.15 / $0.60 M tokens【388918706719218†L150-L159】; it prioritises speed (233 tokens/s) but slightly lower quality【388918706719218†L160-L167】.  Gemini 2.5 Pro focuses on high‑quality reasoning with the same 1 M context. | Gemini 2.5 Pro: $1.25 / $10 M tokens for up to 200 k input tokens; above that the price rises to $2.50 / $15【388918706719218†L216-L224】. | Gemini 2.5 Pro delivers strong reasoning, coding and math performance but at a higher cost and lower output speed (147.7 tokens/s)【388918706719218†L226-L233】. |

### Trade‑offs and recommendation

For summarising and classifying call transcripts, models need to understand conversational context, detect implicit intents and reason about success/failure patterns.  While open models like Llama 4 and Mixtral provide remarkable capabilities at a low cost, the QA task benefits from high‑accuracy reasoning and safety because misclassification can hide customer pain points.  Claude 4 Opus performs best on reasoning and coding benchmarks【286035193800581†L383-L387】 and has a generous 200 k token window【286035193800581†L466-L468】, making it well‑suited for long conversations.  Its input and output costs ($15 / $75 per million tokens) are higher than Mixtral or Llama but lower than GPT‑4.5 preview【286035193800581†L502-L527】.  Claude’s safety mechanisms and enterprise‑focused integrations【286035193800581†L460-L475】 are valuable for a customer‑facing QA system.

OpenAI’s GPT‑4o mini and GPT‑4o offer strong general performance and broad tool support but are more expensive and occasionally hallucinate【286035193800581†L442-L453】.  Gemini 2.5 Flash provides cost‑effective multimodal capabilities but its lower reasoning quality may hinder nuanced classification.  Qwen 3 Max and Llama 4 Maverick are compelling for organisations willing to self‑host or integrate new APIs, though ecosystem maturity and support remain considerations.

**Recommendation:** For a production QA system that balances cost and reasoning accuracy, **Anthropic Claude 4 Sonnet** provides a good compromise: it offers strong reasoning and large context windows at a moderate price ($3 / $15 per million tokens)【286035193800581†L502-L527】.  Organisations with strict budget constraints could pilot **Mixtral 8×7B** or **Llama 4 Maverick**, which deliver excellent price–performance【683397607396387†L21-L33】【230138646397761†L175-L189】.  **OpenAI GPT‑4o** remains a safe choice for generality and integration ease, albeit at higher cost.  Ultimately, the model choice should align with the company’s budget, required reasoning depth and infrastructure preferences.

## Sample analysis results

Below is a summary of the QA system’s output on the provided Nike sample calls using the heuristic fallback (results will be richer when using an LLM).  Each call is tagged with its intent, outcome and rationale, followed by suggested improvements:

| Call | Intent | Outcome | Rationale | Suggested improvements |
|---|---|---|---|---|
| **Call 1** | Order status | Automated – Successful | The AI handled the entire conversation; the customer received the order status and confirmed no further questions. | Continue confirming customer details and summarising the resolution before ending the call. |
| **Call 2** | Return status | Escalated – Partially Successful | The AI sent a returns‑portal link but then escalated when the customer asked for “customer service”. | Provide as much information as possible before escalating; acknowledge frustration and explain why a human agent is needed. |
| **Call 3** | Return status | Escalated – Partially Successful | The AI helped locate the order and sent a returns‑portal link, then transferred when the customer requested a human. | Provide clear refund timelines; empathise with delays; explain the escalation process. |
| **Call 4** | Product question | Escalated – Partially Successful | The AI provided sizing guidance but immediately attempted to transfer to a specialist, then no human was available. | Offer more detailed sizing advice; suggest trying on shoes in store; apologise for human unavailability and provide email support. |
| **Call 5** | Membership question | Escalated – Unsuccessful | The AI immediately transferred to the membership team and no human agent was available. | Explain cancellation steps before escalating; offer alternative contact methods or callbacks; apologise for any inconvenience. |

The LLM‑based analysis would produce more nuanced summaries, classify calls more accurately and generate richer improvement suggestions by reasoning over the full transcript.