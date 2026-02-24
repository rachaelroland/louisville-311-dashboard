# Oliver's Feedback - Quick Summary
## Action Items for Next Revision

**Date:** February 19, 2026
**Status:** 19 Keep, 1 Remove, 1 Uncertain

---

## 🔴 CRITICAL - Must Fix Before Deployment

### 1. REMOVE Question (Unclear)
**waste_schedule_003** - "What are my trash, recycling, or yard waste pickup dates for **this address**?"
- Problem: References "this address" without context - AI doesn't know which address
- Fix: Remove OR rewrite as "How do I find my pickup schedule?"

### 2. WRONG/INCOMPLETE Answers (Need SME Input)
**waste_missed_001** - How to report missed pickup
- Oliver: "Answer is incomplete and wrong"
- Need: SME clarification on correct process

**waste_department_001** - Which department handles waste
- Oliver: "Answer is incomplete and wrong" + "Odd question"
- Need: SME clarification on department info

**waste_forms_001** - Where to find forms
- Oliver: "should explain what waste services DO require paper forms"
- Need: Add info about which services actually need forms

### 3. VERIFY Accuracy
**waste_cart_006** - Extra carts
- Oliver: "not sure 2nd carts are free as noted in the answer"
- Need: SME verification - are additional recycling carts free?

---

## 🟡 CATEGORY FIXES - Consolidate Subcategories

Oliver says these subcategories are "too obscure" - consolidate:

1. **waste_cart_003:** Cart Replacement → **Cart Management**
2. **waste_schedule_002:** Holiday Delay → **Holiday Schedule**
3. **waste_schedule_004:** Cart Placement Timing → **Pickup Schedule**
4. **waste_schedule_005:** Cart Timing - Night Before → **Pickup Schedule**

Optional (Oliver says "might be better"):
5. **waste_hazardous_002:** Paint Disposal → **Hazardous Waste Disposal**
6. **waste_hazardous_003:** Battery Disposal → **Hazardous Waste Disposal**

---

## 💡 STRATEGIC QUESTION - Workflow Integration

**Oliver's comment on 7 questions:**
> "Answer is ok but still sends user to 311; ideally the agent builds out the workflow to handle [X] process"

**Affected Questions:**
- Cart requests (get new, replace damaged, report stolen, get extra)
- Eligibility checks
- Report illegal dumping

**Decision Needed:**
- Should AI just provide information and direct to 311?
- OR should AI actively process requests (submit directly to Metro311 backend)?

This is a **product strategy decision**, not just Q&A content.

---

## ✅ GOOD - No Changes Needed (9 Questions)

Oliver marked "Good answer" with no issues:
- Cart weight limits
- Holiday schedules (both)
- All 4 hazardous waste questions
- Both cart placement timing questions

---

## Summary Stats

**Current Package:** 21 questions
**After Fixes:** ~20 questions

**Changes Required:**
- Remove: 1 question
- Fix answers: 3 questions
- Verify accuracy: 1 question
- Update categories: 4-6 questions
- Strategic decision: 7 questions

---

## Next Steps

1. **Schedule SME meeting** to clarify the 4 critical issues
2. **Decide workflow strategy** with partner/Oliver
3. **Update dataset** based on feedback
4. **Resubmit for approval** (Round 2)

---

**Key Insight:** Most answers are good, but Oliver wants more than just informational Q&A - he wants workflow integration where the AI can actually process service requests, not just direct users to 311.

This may require technical work beyond just Q&A content.
