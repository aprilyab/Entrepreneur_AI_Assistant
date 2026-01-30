#  Entrepreneur AI Assistant

A **LangGraph-based AI assistant** that guides entrepreneurs from idea to actionable business plan using a memory-enabled, decision-driven workflow.

---

##  Features

- Captures startup ideas and optional details.  
- Performs market analysis and business modeling.  
- Provides validation strategies and risk assessment.  
- Generates a **full structured business plan**.  
- Supports follow-up questions after plan generation.  
- Uses memory to track sessions and maintain context.  
- Implements branching decisions based on workflow state.  

---

##  Architecture (All-in-One Flow)

```text
[User Input] 
      │
      ▼
  ┌───────────────┐
  │   Idea Node    │
  └───────────────┘
      │
      ▼
  ┌───────────────────┐
  │ Optional Info Node │
  └───────────────────┘
      │
      ▼
  ┌───────────────────┐
  │ Market Analysis    │
  └───────────────────┘
      │
      ▼
  ┌───────────────────┐
  │ Business Model     │
  └───────────────────┘
      │
      ▼
  ┌───────────────────┐
  │ Validation Node    │
  └───────────────────┘
      │
      ▼
  ┌───────────────────┐
  │ Decision Node      │
  └───────────────────┘
      │
  ┌───┴────────────┐
  ▼                ▼
Risk Node        Growth Node
  │                │
  └──────┬─────────┘
         ▼
  ┌───────────────────┐
  │ Business Plan Node │
  └───────────────────┘
         │
         ▼
  [Follow-up Questions / Memory Enabled]

## Nodes & Responsibilities

| Node Name            | Functionality                                                      |
|----------------------|--------------------------------------------------------------------|
| Idea Node            | Capture the startup idea from the user                             |
| Optional Info Node   | Gather additional optional details                                 |
| Market Analysis Node | Generate market insights and trends                                |
| Business Model Node  | Propose business models (value prop, revenue, pricing, operations) |
| Validation Node      | Suggest ways to validate the idea (MVP, surveys, experiments)      |
| Decision Node        | Decide branch: go to risk assessment or growth                     |
| Risk Node            | Identify potential risks and mitigation plans                      |
| Growth Node          | Suggest scaling/growth strategies                                  |
| Business Plan Node   | Compile a full structured plan from all nodes                      |
| Follow-up Node       | Answer follow-up questions using memory                            |

git clone https://github.com/yourusername/entrepreneur-ai-assistant.git
cd entrepreneur-ai-assistant
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

## 🛠 Installation

```bash
git clone https://github.com/yourusername/entrepreneur-ai-assistant.git
cd entrepreneur-ai-assistant
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```



### Configure .env

```
GEMINI_API_KEY=your_google_generative_api_key
```


## ⚡ Usage

```bash
python -m src.main
```

session_id

## Workflow Example

**Input:** "I want to start a small cloth shop"

1. **Idea Node** → Captures the idea
2. **Optional Info Node** → Gather target customers
3. **Market Analysis Node** → Market insights
4. **Business Model Node** → Value proposition, revenue streams
5. **Validation Node** → Suggest MVP testing
6. **Decision Node** → Choose Risk Assessment or Growth path
7. **Risk Node** → Identify risks
8. **Business Plan Node** → Generate full plan
9. **Follow-up** → Ask questions based on plan

---

## Memory & State

Memory Store keeps previous sessions:
    - `session_id`
    - `user_name`
    - `idea`
    - `final_plan`

Supports:


- Context-aware follow-ups
- Tracking user progress
- Dynamic branching decisions

---

## Branching Logic

- Market-first or Business Model-first based on state `branch_to_market`.
- Risk assessment or Growth path based on `go_to_risk`.
- Enables dynamic, user-driven workflow.


---

## Example Output

### === Full Business Plan ===

**Idea:** Small cloth shop

**Market Analysis:**
    - Local demand for handmade clothing
    - Competitors: X, Y, Z
    - Opportunities: online sales, eco-friendly materials

**Business Model:**
    - Value proposition: unique, sustainable fashion
    - Customer segments: local youth, online buyers
    - Revenue streams: online sales, in-store
    - Pricing: $20-$50 per item

**Validation:**
    - Launch pilot collection
    - Gather feedback from first 50 customers

**Risk Assessment:**
    - Low foot traffic risk
    - Supply chain delays

**Next Steps:**
    - Build team
    - Create marketing campaign
    - Track metrics

**Follow-up Question:** "How to attract first 100 customers?"
**Answer:**
    - Use social media campaigns targeting local youth
    - Collaborate with influencers
    - Offer launch discounts

---

## Future Improvements

- Web-based UI using Streamlit or Gradio
- Enhanced memory for cross-session learning
- More specialized nodes: marketing, finance, operations
- Export plan to PDF or Word automatically
