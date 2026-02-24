# Oliver's Feedback Analysis & Action Plan
## Waste Management Q&A Package - February 18, 2026

**Reviewed by:** Oliver (OA)
**Total Questions Reviewed:** 21
**Status Summary:**
- ✅ Keep: 19 questions
- ❌ Remove: 1 question
- ⚠️ Uncertain: 1 question

---

## Critical Issues Requiring Action

### 1. **REMOVE - Question Unclear**
**waste_schedule_003** - "What are my trash, recycling, or yard waste pickup dates for this address?"
- **Oliver's Feedback:** "Question is unclear" + "Question and Answer not great"
- **Action:** REMOVE this question or completely rewrite
- **Issue:** The question references "this address" but AI doesn't have context of which address
- **Alternative:** Change to "How do I find my trash/recycling/yard waste pickup schedule?"

---

### 2. **INCOMPLETE & WRONG ANSWERS - Fix Required**

#### waste_missed_001 - Missed Pickup
- **Oliver's Feedback:** "Answer is incomplete and wrong"
- **Current Issue:** Unknown - need to verify what's wrong
- **Action Required:** Get SME clarification on correct missed pickup process

#### waste_department_001 - Department Info
- **Oliver's Feedback:** "Answer is incomplete and wrong" + "Odd question"
- **Current Issue:** Unknown - need to verify what's missing/wrong
- **Action Required:** Get SME clarification on department structure and contact info

---

### 3. **INCOMPLETE - Missing Information**

#### waste_forms_001 - Forms & Resources
- **Oliver's Feedback:** "Question lacks specificity" + "answer should explain what waste services DO require paper forms"
- **Current Answer:** Only says "most don't require forms"
- **Action Required:** Add information about which services actually DO require forms (e.g., Waste Set-Out Variance, special accommodations, etc.)

---

### 4. **VERIFY ACCURACY**

#### waste_cart_006 - Extra Cart
- **Oliver's Feedback:** "needs to be verified b/c I'm not sure 2nd carts are free as noted in the answer"
- **Current Answer:** Says "additional recycling carts are typically provided FREE"
- **Action Required:** SME verification - are additional recycling carts actually free? What about trash carts?

---

## Category Adjustments Required

### Consolidate Subcategories (Too Obscure)

**Issue:** Multiple overly specific subcategories that should be consolidated

#### Changes Needed:

1. **waste_cart_003** - "Cart Replacement" → **"Cart Management"**
   - Current: Cart Replacement
   - Change to: Cart Management
   - Reason: Consolidate all cart-related questions

2. **waste_schedule_002** - "Holiday Delay" → **"Holiday Schedule"**
   - Current: Holiday Delay
   - Change to: Holiday Schedule
   - Reason: Merge with waste_schedule_001 (similar questions)

3. **waste_hazardous_002** - "Paint Disposal" → **"Hazardous Waste Disposal"**
   - Current: Paint Disposal
   - Change to: Hazardous Waste Disposal (consider)
   - Reason: More consistent categorization

4. **waste_hazardous_003** - "Battery Disposal" → **"Hazardous Waste Disposal"**
   - Current: Battery Disposal
   - Change to: Hazardous Waste Disposal (consider)
   - Reason: More consistent categorization

5. **waste_schedule_004** - "Cart Placement Timing" → **"Pickup Schedule" or "Cart Management"**
   - Current: Cart Placement Timing
   - Change to: Pickup Schedule
   - Reason: Category too obscure

6. **waste_schedule_005** - "Cart Timing - Night Before" → **"Pickup Schedule" or "Cart Management"**
   - Current: Cart Timing - Night Before
   - Change to: Pickup Schedule
   - Reason: Category too obscure

---

## Strategic Feedback - Workflow Integration

**Oliver's Recurring Comment (7 instances):**
> "Answer is ok but still sends user to 311; ideally the agent builds out the workflow to handle [X] process"

### Questions Affected:
1. waste_cart_002 - Get recycling cart
2. waste_cart_003 - Replace damaged cart
3. waste_cart_004 - Report stolen cart
4. waste_cart_006 - Get extra cart
5. waste_eligibility_001 - Check address eligibility
6. waste_dumping_001 - Report illegal dumping

**Implication:** Oliver wants the AI to actually execute workflows, not just direct to 311

**Options:**
- **Option A:** Leave as-is (informational answers directing to 311)
- **Option B:** Build integrated workflows where AI can submit requests directly
- **Option C:** Hybrid - AI asks for information, confirms details, then submits to 311 system

**Decision Required:** Is the AI just answering questions OR actively handling service requests?

---

## Good Answers - No Changes Needed

**Oliver marked "Good answer" for:**
- ✅ waste_cart_005 - Cart weight limits
- ✅ waste_schedule_001 - Holiday pickup (though similar to 002)
- ✅ waste_schedule_002 - Holiday delays (though similar to 001)
- ✅ waste_hazardous_001 - Hazardous waste disposal
- ✅ waste_hazardous_002 - Paint disposal
- ✅ waste_hazardous_003 - Battery disposal
- ✅ waste_hazardous_004 - Electronics disposal
- ✅ waste_schedule_004 - Cart placement timing
- ✅ waste_schedule_005 - Night before placement

---

## Questionable Decision

**waste_forms_001 - "?" (Uncertain)**
- Oliver uncertain whether to keep this question
- Feedback: "Question lacks specificity" + answer incomplete
- **Recommendation:** Either improve significantly or remove

---

## Summary of Required Actions

### Immediate Actions (Before Deployment)

1. **REMOVE** waste_schedule_003 (pickup dates - unclear question)
2. **FIX** waste_missed_001 - Get SME input on what's wrong/incomplete
3. **FIX** waste_department_001 - Get SME input on what's wrong/incomplete
4. **IMPROVE** waste_forms_001 - Add info about which services DO require forms
5. **VERIFY** waste_cart_006 - Confirm if 2nd recycling carts are actually free

### Category Consolidation

6. **UPDATE** 6 subcategories to be less obscure:
   - Cart Replacement → Cart Management
   - Holiday Delay → Holiday Schedule
   - Paint Disposal → Hazardous Waste Disposal (maybe)
   - Battery Disposal → Hazardous Waste Disposal (maybe)
   - Cart Placement Timing → Pickup Schedule
   - Cart Timing - Night Before → Pickup Schedule

### Strategic Discussion Required

7. **DISCUSS** workflow integration approach with partner
   - Should AI just inform OR actively process requests?
   - 7 questions affected by this decision
   - May require technical integration work

---

## Revised Package Status

**Current State:**
- 21 questions submitted
- 1 question to remove (waste_schedule_003)
- 3 questions need major fixes (missed_001, department_001, forms_001)
- 1 question needs verification (cart_006)
- 6 questions need category updates

**Next State (Post-Fixes):**
- ~20 questions (after removing schedule_003)
- All answers verified correct by SME
- Categories consolidated and clearer
- Decision made on workflow integration approach

---

## Recommended Next Steps

### Step 1: SME Validation Meeting (2-3 hours)
**Agenda:**
1. Review the 3 "incomplete and wrong" answers - what needs to change?
2. Verify extra cart pricing (waste_cart_006)
3. Identify which services DO require paper forms (waste_forms_001)
4. Discuss workflow integration vs. informational approach
5. Review consolidated categories for approval

### Step 2: Update Dataset (1-2 hours)
1. Remove waste_schedule_003
2. Fix 3 incomplete/wrong answers based on SME input
3. Update waste_forms_001 with complete information
4. Consolidate 6 subcategories
5. Create updated CSV

### Step 3: Partner Review Round 2 (30 min)
- Share updated dataset (~20 questions)
- Confirm all feedback addressed
- Get final approval for deployment

### Step 4: Deploy to Production (1 hour)
- Insert validated Q&As into database
- Test with sample queries
- Monitor accuracy

---

## Questions for Oliver/SME

1. **waste_missed_001:** What specifically is incomplete or wrong about the missed pickup answer?
2. **waste_department_001:** What information is missing about the department?
3. **waste_forms_001:** Which waste services actually DO require paper forms?
4. **waste_cart_006:** Are additional recycling carts really free? What about trash carts?
5. **Workflow Integration:** Should the AI actively process requests (submit to Metro311 backend) or just provide information and direct to 311?
6. **Similar Questions (schedule_001 & 002):** Should these be merged into one question?

---

**Analysis Prepared By:** Rachael + Claude Code
**Date:** February 19, 2026
**Next Action:** Schedule SME meeting to address feedback items
