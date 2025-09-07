# tools.py
# Advanced tools for Grab's AI customer service agent
# Now integrated with realistic sandbox environment

import random
from datetime import datetime, timedelta
import sys
import os

# Add sandbox directory to Python path
sandbox_path = os.path.join(os.path.dirname(__file__), 'sandbox')
if sandbox_path not in sys.path:
    sys.path.insert(0, sandbox_path)

try:
    from sandbox_database import sandbox_db
    from sandbox_tools import (
        get_customer_profile, get_order_investigation, 
        process_customer_refund, log_merchant_quality_issue,
        exonerate_delivery_partner, check_refund_eligibility,
        get_merchant_substitute_policy
    )
    SANDBOX_AVAILABLE = True
    print("✓ Sandbox environment loaded successfully")
except ImportError as e:
    print(f"⚠ Sandbox not available: {e}")
    SANDBOX_AVAILABLE = False

def collect_evidence(query: str) -> str:
    """
    Analyze the customer's complaint and determine if we have enough information to proceed
    """
    # Handle null or placeholder inputs
    if not query or query.lower() in ["null", "none", ""]:
        query = "general complaint"
    
    print(f"--- Analyzing Customer Complaint: {query} ---")
    
    # Check if the query contains sufficient information to proceed
    has_order_info = any(keyword in query.lower() for keyword in ["order", "paid", "rupees", "rs", "$", "restaurant", "kitchen"])
    has_issue_info = any(keyword in query.lower() for keyword in ["wrong", "late", "delay", "cold", "missing", "quality", "spilled"])
    
    if has_order_info and has_issue_info:
        return f"""COMPLAINT ANALYSIS COMPLETE:
        
Based on your description, I have sufficient information to help you:
• Issue Type: {query}
• Status: Ready to provide solution
• Next Step: Processing appropriate compensation

I can now offer you a resolution for this issue."""
    
    return """INFORMATION GATHERING:

To help you effectively, I need to understand:
• What items did you order?
• How much did you pay?
• What specific issue occurred?
• Which restaurant was it from?

Please provide these details so I can assist you properly."""

def calculate_dynamic_compensation(issue_type: str, order_value: float = None) -> dict:
    """Calculate dynamic compensation based on issue type and context"""
    
    # Base compensation matrix
    compensation_matrix = {
        "spilled": {"base": 1.0, "bonus": 50, "type": "full_refund_plus"},
        "damaged": {"base": 1.0, "bonus": 30, "type": "full_refund_plus"},
        "wrong_order": {"base": 1.0, "bonus": 20, "type": "full_refund"},
        "missing_items": {"base": 0.6, "bonus": 15, "type": "partial_refund"},
        "cold_food": {"base": 0.4, "bonus": 25, "type": "partial_refund"},
        "late_delivery": {"base": 0.3, "bonus": 10, "type": "delivery_refund"},
        "poor_quality": {"base": 0.7, "bonus": 20, "type": "partial_refund"}
    }
    
    # Estimated order values for dynamic calculation
    estimated_orders = [180, 250, 320, 450, 580, 720, 890, 1200]
    order_value = order_value or random.choice(estimated_orders)
    
    # Get compensation details
    comp = compensation_matrix.get(issue_type, {"base": 0.5, "bonus": 15, "type": "standard"})
    
    refund_amount = int(order_value * comp["base"])
    bonus_voucher = comp["bonus"]
    total_value = refund_amount + bonus_voucher
    
    return {
        "order_value": order_value,
        "refund_amount": refund_amount,
        "bonus_voucher": bonus_voucher,
        "total_compensation": total_value,
        "compensation_type": comp["type"]
    }

def generate_personalized_response(issue_type: str, weather_factor: bool = False) -> str:
    """Generate personalized, contextual responses"""
    
    # Weather-based empathy responses
    weather_responses = [
        "I can see it's been quite rainy today - that definitely made deliveries more challenging!",
        "With this heavy rain, our delivery partners are doing their best to stay safe while getting your food to you.",
        "The weather has been particularly difficult today, causing some delays across the city.",
        "Given the storm conditions, I completely understand your frustration with the timing."
    ]
    
    # Personality-driven responses by issue type
    response_styles = {
        "spilled": [
            "Oh no! That's absolutely devastating - there's nothing worse than eagerly waiting for your meal only to have it arrive damaged.",
            "I'm genuinely upset hearing this happened to you! A spilled meal completely ruins the whole experience.",
            "This is exactly the kind of situation that makes my day difficult - I'm so sorry this happened!"
        ],
        "wrong_order": [
            "Ugh, getting the wrong order is like unwrapping a present and finding socks instead of what you actually wanted!",
            "I can only imagine the disappointment - you were probably really looking forward to your specific meal!",
            "Mix-ups like this are incredibly frustrating, especially when you've got your heart set on something particular."
        ],
        "late_delivery": [
            "Time is precious, and we definitely didn't respect yours today. That's on us!",
            "I know how annoying it is to keep checking your phone wondering where your food is!",
            "Hunger + waiting = the worst combination. I completely get why you're frustrated."
        ],
        "cold_food": [
            "Cold food is just... sad food. Nobody should have to eat a lukewarm meal they paid good money for!",
            "There's something particularly disappointing about food that's lost its warmth - it changes the whole experience.",
            "A hot meal arriving cold is honestly one of the most deflating things in food delivery."
        ]
    }
    
    # Select appropriate response style
    if weather_factor and issue_type == "late_delivery":
        base_response = random.choice(weather_responses)
        empathy = random.choice(response_styles.get(issue_type, ["I understand your frustration."]))
        return f"{base_response} {empathy}"
    else:
        return random.choice(response_styles.get(issue_type, ["I understand your frustration and want to make this right."]))

def analyze_customer_situation(customer_message: str) -> str:
    """
    Business-first analysis that requests evidence and directs to proper workflow
    """
    print(f"--- Business Analysis: {customer_message} ---")
    
    # Extract key information from the customer's message
    message_lower = customer_message.lower()
    
    # Determine if this is a tracking request or actual problem
    tracking_keywords = ["where", "status", "driver", "eta", "time", "location"]
    problem_keywords = ["spill", "wrong", "damage", "cold", "missing", "terrible", "awful", "bad", "broken", "packaging"]
    
    is_tracking_request = any(word in message_lower for word in tracking_keywords) and not any(word in message_lower for word in problem_keywords)
    is_actual_problem = any(word in message_lower for word in problem_keywords)
    
    if is_tracking_request:
        return f"""🎯 TRACKING REQUEST DETECTED:
        
✅ Customer wants: ORDER LOCATION INFORMATION
❌ Customer does NOT want: Compensation

🚀 BUSINESS ACTION REQUIRED:
• Use track_delivery_status() IMMEDIATELY
• Provide actual delivery location and timing
• Only offer small gesture voucher if delay >45 minutes
• AVOID any compensation discussions

💡 Remember: Customer asking "where is my order?" wants INFORMATION, not money!"""
    
    elif is_actual_problem:
        # Determine if visual evidence would help
        evidence_needed_cases = ["spill", "damage", "wrong", "packaging", "quality", "broken", "mess", "bad"]
        needs_evidence = any(word in message_lower for word in evidence_needed_cases)
        
        issue_type = "general_problem"
        if any(word in message_lower for word in ["spill", "damage", "leak", "mess"]):
            issue_type = "spilled_food"
        elif any(word in message_lower for word in ["wrong", "different", "mistake"]):
            issue_type = "wrong_order"
        elif any(word in message_lower for word in ["packaging", "broken", "damaged"]):
            issue_type = "packaging_issue"
        elif any(word in message_lower for word in ["cold", "lukewarm"]):
            issue_type = "cold_food"
        elif any(word in message_lower for word in ["missing", "forgot"]):
            issue_type = "missing_items"
        elif any(word in message_lower for word in ["quality", "bad", "terrible"]):
            issue_type = "quality_issue"
        
        evidence_instruction = ""
        if needs_evidence:
            evidence_instruction = f"""
📸 **EVIDENCE COLLECTION REQUIRED:**
• Request customer to upload photo evidence
• Visual proof helps with accurate assessment
• Say: "Could you please share a photo of the issue? This will help me understand the situation better and ensure appropriate resolution."
• WAIT for evidence before proceeding to compensation
"""
        
        return f"""🎯 ACTUAL PROBLEM DETECTED:
        
✅ Issue Type: {issue_type.replace('_', ' ').title()}
🚨 Business Priority: SYMPATHIZE → LOG INCIDENT → ONLY COMPENSATE IF EXPLICITLY REQUESTED

{evidence_instruction}

🚀 CONSERVATIVE BUSINESS WORKFLOW:
1. Express genuine empathy and apology for the experience
2. Log the incident and report it to the merchant for improvement
3. Assure customer that feedback helps us improve service quality
4. DO NOT mention compensation, refunds, or any monetary remedies
5. ONLY if customer explicitly asks for refund → use gather_compensation_details
6. When negotiating compensation → maximum 50% of order value
7. If customer unsatisfied with 50% offer → escalate to human agent

💼 FORBIDDEN: 
• Proactive compensation offers without customer request
• Mentioning refunds, compensation, or money in initial response
• Offering more than 50% of order value as compensation
• Processing compensation without explicit customer request

💡 Remember: Be sympathetic but don't offer money unless specifically asked!"""
    
    else:
        return f"""🎯 GENERAL INQUIRY DETECTED:
        
✅ Customer Message: "{customer_message}"
🚀 ACTION: Gather more context before proceeding

💡 Ask customer to clarify:
• Are you tracking an order?
• Is there an issue with your delivery?
• What specific assistance do you need?"""
    
    # Classify severity dynamically
    if issue_type in ["spilled", "damaged"]:
        severity = "CRITICAL"
        action_urgency = "IMMEDIATE FULL RESOLUTION"
    elif issue_type in ["wrong_order", "missing_items"]:
        severity = "HIGH"
        action_urgency = "PRIORITY RESOLUTION"
    elif issue_type in ["late_delivery", "cold_food"]:
        severity = "MEDIUM"
        action_urgency = "PROMPT RESOLUTION"
    else:
        severity = "STANDARD"
        action_urgency = "STANDARD RESOLUTION"
    
    return f"""✅ DYNAMIC ANALYSIS COMPLETE:

🎯 Issue Detected: {issue_type.replace('_', ' ').title()}
🚨 Severity: {severity}
� Customer Sentiment: {empathy_response}

� SMART COMPENSATION CALCULATED:
• Order Value: ₹{compensation['order_value']}
• Refund Amount: ₹{compensation['refund_amount']}
• Bonus Voucher: ₹{compensation['bonus_voucher']}
• Total Value: ₹{compensation['total_compensation']}

⚡ Action Required: {action_urgency}
🚀 RECOMMENDATION: PROCEED WITH PERSONALIZED SOLUTION
• No additional details needed
• Time to resolve and compensate

NEXT ACTION: Use provide_generic_solution to fix this issue now!"""

def ask_for_order_details(context: str) -> str:
    """Ask the customer for specific order details to better assist them"""
    print(f"--- Requesting Order Details: {context} ---")
    
    return """I'd be happy to help you with your order issue! To provide the best assistance, could you please share:

1. **What did you order?** (specific items/dishes)
2. **Order amount?** (total you paid)
3. **What went wrong?** (wrong item, late delivery, quality issue, missing items, etc.)
4. **Restaurant name?** (which merchant/restaurant)
5. **When did this happen?** (today, yesterday, specific time)

With these details, I can investigate your concern and offer an appropriate solution like a refund, reorder, or other compensation."""

def handle_wrong_order_situation(order_details: str) -> str:
    """Handle wrong order complaints by offering choices before processing refunds"""
    print(f"--- Handling Wrong Order: {order_details} ---")
    
    return f"""I'm really sorry about the wrong order mix-up! That's definitely frustrating when you're expecting one thing and get something completely different.

🎯 **Here are your options:**

**Option 1: Get the Correct Order**
• I can arrange for your original pizza from Dominos to be prepared and delivered
• This would be at no extra charge, and we'll prioritize it
• Estimated time: 25-30 minutes

**Option 2: Keep Current Order + Partial Refund** 
• You can keep the McDonald's burgers (if you want them)
• I'll process a partial refund for the difference
• Quick resolution without waiting

**Option 3: Full Refund**
• Complete refund of ₹200 to your original payment method
• You can reorder whatever you'd like
• Refund processes in 2-3 business days

**What would work best for you?** I'm here to make this right in whatever way you prefer!

(I won't process anything until you let me know what you'd like to do)"""

def provide_generic_solution(issue_details: str) -> str:
    """Conservative business response that expresses sympathy and logs incident without offering compensation"""
    print(f"--- Conservative Business Response Strategy: {issue_details} ---")
    
    # Parse the issue type from details
    details_lower = issue_details.lower()
    
    # Determine issue type
    issue_type = "general"
    if any(word in details_lower for word in ["spill", "damage", "leak", "mess"]):
        issue_type = "spilled_food"
    elif any(word in details_lower for word in ["wrong", "different", "not what", "mistake"]):
        issue_type = "wrong_order"
    elif any(word in details_lower for word in ["late", "delay", "slow", "waiting"]):
        issue_type = "late_delivery"
    elif any(word in details_lower for word in ["cold", "lukewarm", "not hot"]):
        issue_type = "cold_food"
    elif any(word in details_lower for word in ["missing", "forgot", "didn't get"]):
        issue_type = "missing_items"
    
    # Conservative, sympathetic responses that log incidents without offering compensation
    if issue_type == "spilled_food":
        return f"""I'm truly sorry to hear about your food being spilled during delivery. I completely understand how disappointing and frustrating this must be, especially after you were looking forward to your meal.

📋 **What I'm doing right now:**
• **Logging this incident** with our quality assurance team
• **Reporting to the merchant** to prevent similar issues
• **Documenting delivery partner feedback** for improvement
• **Adding this to our quality improvement database**

This kind of feedback is incredibly valuable for helping us improve our service standards. Your experience helps us train our delivery partners better and work with merchants on proper packaging.

📝 **Incident Status:** Recorded and forwarded to relevant teams for review

Is there anything else about this experience you'd like me to document or address?"""

    elif issue_type == "wrong_order":
        return f"""I sincerely apologize for the mix-up with your order. Receiving something different from what you ordered is definitely frustrating, and I completely understand your disappointment.

📋 **What I'm doing right now:**
• **Logging this order error** in our system for investigation
• **Notifying the merchant** about the preparation mistake
• **Recording this feedback** to improve order accuracy
• **Updating quality metrics** to prevent future mix-ups

Your feedback is essential for helping us improve our order fulfillment process. This information helps both our restaurant partners and our operations team understand where improvements are needed.

📝 **Incident Status:** Documented and shared with quality improvement team

Is there anything specific about the order mix-up you'd like me to include in the report?"""

    elif issue_type == "cold_food":
        return f"""I'm really sorry your food arrived cold. I know how disappointing it is when your meal doesn't arrive at the right temperature - it really affects the whole dining experience.

📋 **What I'm doing right now:**
• **Recording this temperature issue** for delivery quality review
• **Informing the merchant** about food temperature maintenance
• **Logging delivery time factors** that may have contributed
• **Adding to our service improvement tracking**

This type of feedback helps us work with both restaurants and delivery partners on maintaining food quality during transport. Your input is valuable for improving our overall service standards.

📝 **Incident Status:** Logged for quality assurance follow-up

Would you like me to include any additional details about the delivery timing or food condition?"""

    elif issue_type == "late_delivery":
        return f"""I apologize for the delayed delivery of your order. I understand how inconvenient it is when your food takes longer than expected, especially when you're hungry and planning your time around the delivery.

📋 **What I'm doing right now:**
• **Recording this delivery delay** for route optimization review
• **Analyzing the delivery timeline** to identify causes
• **Documenting for delivery partner performance review**
• **Logging for operational efficiency improvements**

Your feedback about delivery timing helps us improve our logistics and better manage customer expectations. This information is valuable for optimizing our delivery operations.

📝 **Incident Status:** Documented for operational review and improvement

Is there anything else about the delivery experience you'd like me to record?"""

    elif issue_type == "missing_items":
        return f"""I'm sorry some items were missing from your order. I understand how frustrating it is when you're expecting certain items and they're not included in your delivery.

📋 **What I'm doing right now:**
• **Logging this missing items incident** for quality control
• **Notifying the merchant** about order completeness procedures
• **Recording for delivery verification process improvement**
• **Documenting for order fulfillment training**

This feedback is crucial for helping us improve our order verification processes with restaurant partners. Your experience helps us strengthen quality control measures.

📝 **Incident Status:** Recorded for merchant and operations team review

Would you like me to document any other details about what was missing?"""

    else:
        return f"""I'm sorry to hear about the issue with your order. I understand your frustration and want to make sure we properly document what happened to help improve our service.

📋 **What I'm doing right now:**
• **Logging your feedback** in our quality improvement system
• **Recording the incident details** for review by relevant teams
• **Documenting for service enhancement** and training purposes
• **Adding to our customer experience tracking**

Your feedback is valuable for helping us identify areas where we can do better. This information helps us improve our service for all customers.

📝 **Incident Status:** Documented and forwarded for appropriate follow-up

Is there anything specific about your experience you'd like me to include in the report?"""


def handle_edge_cases(message: str) -> dict:
    """Handle humor, vague complaints, slang, and incomplete information naturally"""
    
    message_lower = message.lower()
    
    # Humor detection
    humor_indicators = ["lol", "haha", "😂", "😅", "funny", "joke", "kidding"]
    if any(indicator in message_lower for indicator in humor_indicators):
        return {
            "type": "humor",
            "response_style": "playful",
            "suggested_tone": "Match their energy while being helpful"
        }
    
    # Slang detection
    slang_map = {
        "food is trash": "poor quality food",
        "driver is sus": "suspicious driver behavior", 
        "this is cap": "this seems wrong",
        "no cap": "honestly",
        "bet": "okay/sure",
        "fire food": "excellent food",
        "mid": "mediocre/average",
        "lowkey": "somewhat/kind of",
        "highkey": "very/really",
        "slaps": "really good",
        "bussin": "really good/delicious",
        "periodt": "end of discussion"
    }
    
    translated_message = message_lower
    slang_found = []
    for slang, meaning in slang_map.items():
        if slang in message_lower:
            translated_message = translated_message.replace(slang, meaning)
            slang_found.append(slang)
    
    # Vague complaint detection
    vague_indicators = ["bad", "terrible", "awful", "horrible", "not good", "disappointing"]
    is_vague = any(indicator in message_lower for indicator in vague_indicators) and len(message.split()) < 8
    
    # Incomplete information detection
    question_words = ["what", "when", "where", "how", "why"]
    has_questions = any(word in message_lower for word in question_words)
    is_incomplete = len(message.split()) < 5 or has_questions
    
    return {
        "original_message": message,
        "translated_message": translated_message,
        "slang_detected": slang_found,
        "is_vague": is_vague,
        "is_incomplete": is_incomplete,
        "has_humor": len([h for h in humor_indicators if h in message_lower]) > 0,
        "response_style": "casual" if slang_found else "professional"
    }

def generate_natural_response(issue_type: str, edge_case_info: dict) -> str:
    """Generate natural responses based on communication style and edge cases"""
    
    # Casual/slang responses
    if edge_case_info["response_style"] == "casual":
        casual_intros = {
            "spilled": "Yooo, that's actually terrible! Food everywhere is NOT the vibe 😭",
            "wrong_order": "Bruh, getting the wrong order hits different when you're hungry! That's on us fr",
            "late_delivery": "Okay that wait time is lowkey unacceptable, my bad on that one!",
            "cold_food": "Cold food is just... nah. That's not it, chief. Let me fix this for real",
            "poor_quality": "If the food was mid/trash, that's totally our fault - we gotta make this right!"
        }
        return casual_intros.get(issue_type, "My bad, let me make this right for you!")
    
    # Vague complaint handling
    elif edge_case_info["is_vague"]:
        empathetic_responses = [
            "I can tell you're frustrated, and that's completely valid! Even though I don't have all the details, I want to help you right away.",
            "Something clearly went wrong with your experience, and I'm sorry about that! Let me see what I can do to make you feel better.",
            "I hear the disappointment in your message, and I want to turn this around for you immediately!"
        ]
        return random.choice(empathetic_responses)
    
    # Humor/playful tone
    elif edge_case_info["has_humor"]:
        playful_responses = {
            "spilled": "Haha, okay but seriously - spilled food is like a tragedy with a side of mess! Let me fix this disaster 😄",
            "wrong_order": "LOL I wish mix-ups were actually funny, but when you're hungry it's just cruel! Let me sort this out",
            "late_delivery": "Right? The waiting game is NOT fun when food is involved! Time to make this worth the wait",
        }
        return playful_responses.get(issue_type, "I appreciate you keeping it light! Let me make sure this ends on a high note 😊")
    
    # Professional but warm default
    else:
        return "I understand your concern and I'm here to help resolve this for you right away."

def check_customer_history(customer_id: str) -> str:
    """Check customer's order history and complaint patterns with sandbox data."""
    print(f"--- Checking Customer History: {customer_id} ---")
    
    if SANDBOX_AVAILABLE:
        return get_customer_profile(customer_id)
    
    # Fallback for non-sandbox mode
    profiles = [
        "Premium customer (50+ orders, 4.8/5 rating, 1 complaint in 6 months) - High trust level",
        "Regular customer (15 orders, 4.2/5 rating, 2 complaints resolved) - Normal trust level", 
        "New customer (3 orders, no ratings, first complaint) - Standard verification needed",
        "Frequent complainer (20 orders, 3.1/5 rating, 8 complaints) - Enhanced verification required"
    ]
    
    return f"Customer Profile: {random.choice(profiles)}"

def issue_instant_refund(refund_details: str) -> str:
    """Issue instant refund with proper documentation using sandbox."""
    try:
        customer_id, amount, reason = refund_details.split(',', 2)
        amount = float(amount.strip())
        reason = reason.strip()
        
        print(f"--- Processing Refund: ${amount} to {customer_id} for {reason} ---")
        
        if SANDBOX_AVAILABLE:
            return process_customer_refund(customer_id, amount, reason)
        
        # Fallback
        return f"Instant refund of ₹{amount} processed for customer {customer_id}. Reason: {reason}. Funds will appear in 1-3 business days."
    except:
        return "Error: Please provide refund details as customer_id,amount,reason"

def exonerate_driver(driver_details: str) -> str:
    """Clear driver of fault with documentation using sandbox."""
    driver_id, reason = driver_details.split(',', 1) if ',' in driver_details else (driver_details, "Evidence supports innocence")
    print(f"--- Exonerating Driver {driver_id}: {reason} ---")
    
    if SANDBOX_AVAILABLE:
        return exonerate_delivery_partner(driver_id, reason)
    
    # Fallback
    return f"Driver {driver_id} cleared of all fault. Reason: {reason}. No impact on performance record."

def log_merchant_packaging_feedback(feedback_details: str) -> str:
    """Log detailed merchant feedback for quality improvement using sandbox."""
    try:
        merchant_id, feedback = feedback_details.split(',', 1)
        print(f"--- Logging Merchant Feedback: {merchant_id} ---")
        
        if SANDBOX_AVAILABLE:
            return log_merchant_quality_issue(merchant_id.strip(), feedback.strip(), "high")
        
        # Fallback
        return f"Quality feedback logged for merchant {merchant_id.strip()}: '{feedback.strip()}'. Forwarded to merchant quality team for review and improvement action."
    except:
        return "Error: Please provide feedback as merchant_id,feedback_details"

# New sandbox-specific tools for advanced reasoning

def analyze_order_discrepancy(order_id: str) -> str:
    """Analyze what went wrong with a specific order"""
    # Handle placeholder inputs
    if not order_id or "obtained from" in order_id.lower() or order_id.lower() in ["null", "none"]:
        order_id = "ORD_001"  # Default to first sandbox order
    
    print(f"--- Analyzing Order Discrepancy: {order_id} ---")
    
    if SANDBOX_AVAILABLE:
        return get_order_investigation(order_id)
    
    return f"""Order Analysis for {order_id}:
    • Order Status: Completed with customer complaint
    • Issue Type: Wrong items delivered
    • Expected: Pizza Margherita
    • Received: Burger Combo
    • Root Cause: Kitchen preparation error
    • Recommendation: Full refund + merchant feedback"""

def assess_refund_eligibility(eligibility_details: str) -> str:
    """Assess customer eligibility for refund based on history and order details"""
    # Parse input or use defaults
    try:
        if ',' in eligibility_details:
            parts = eligibility_details.split(',')
            customer_id = parts[0].strip() if len(parts) > 0 else "C001"
            order_id = parts[1].strip() if len(parts) > 1 else "ORD_001"
            requested_amount = float(parts[2].strip()) if len(parts) > 2 else 450.0
        else:
            customer_id = "C001"
            order_id = "ORD_001"
            requested_amount = 450.0
    except:
        customer_id = "C001"
        order_id = "ORD_001"
        requested_amount = 450.0
    
    print(f"--- Assessing Refund Eligibility for {customer_id} ---")
    
    if SANDBOX_AVAILABLE:
        try:
            from sandbox_tools import check_refund_eligibility
            return check_refund_eligibility(customer_id, order_id, requested_amount)
        except:
            pass
    
    return f"""Refund Eligibility Assessment:
    • Customer: {customer_id}
    • Order: {order_id}
    • Requested Amount: ₹{requested_amount}
    • Customer Status: Premium (50+ orders, high rating)
    • Complaint History: Minimal (first complaint in 6 months)
    • Order Verification: Valid complaint confirmed
    • Eligibility: APPROVED - Full refund authorized
    • Processing Time: Instant (2-3 business days to reflect)"""

def check_merchant_substitution_policy(merchant_id: str, original_item: str) -> str:
    """Check merchant's item substitution policy"""
    print(f"--- Checking Substitution Policy: {merchant_id} ---")
    
    if SANDBOX_AVAILABLE:
        try:
            from sandbox_tools import get_merchant_substitute_policy
            return get_merchant_substitute_policy(merchant_id, original_item)
        except:
            pass
    
    return f"Substitution policy for {merchant_id}: Standard merchant substitution guidelines apply."

def validate_customer_complaint(complaint_details: str) -> str:
    """Validate customer complaint against order history and delivery logs"""
    # Default customer ID if not provided
    customer_id = "C001"
    
    # Handle missing complaint details
    if not complaint_details or complaint_details.lower() in ["null", "none"]:
        complaint_details = "Customer reported wrong order received"
    
    print(f"--- Validating Complaint from {customer_id} ---")
    
    if SANDBOX_AVAILABLE:
        customer_profile = get_customer_profile(customer_id)
        return f"COMPLAINT VALIDATION:\n{customer_profile}\n\nComplaint Details: {complaint_details}\nValidation Status: Cross-referenced with order history and delivery logs."
    
    return f"""Complaint Validation for {customer_id}:
    • Complaint: {complaint_details}
    • Customer Status: Premium customer (50+ orders)
    • Complaint History: First complaint in 6 months
    • Order History: Consistent positive feedback
    • Validation: LEGITIMATE - Customer has strong track record
    • Recommendation: Process refund immediately"""

def check_driver_history(driver_id: str) -> str:
    """Check driver's performance and incident history."""
    print(f"--- Checking Driver History: {driver_id} ---")
    
    profiles = [
        "Experienced driver (4.9/5 rating, 2000+ deliveries, 0 incidents this month) - Highly reliable",
        "Good driver (4.6/5 rating, 500 deliveries, 1 minor incident) - Generally reliable",
        "New driver (4.3/5 rating, 50 deliveries, learning phase) - Normal monitoring",
        "Problematic driver (4.0/5 rating, 200 deliveries, 3 incidents this month) - Under review"
    ]
    
    return f"Driver Profile: {random.choice(profiles)}"

def check_merchant_history(merchant_id: str) -> str:
    """Check merchant's quality ratings and issue history."""
    print(f"--- Checking Merchant History: {merchant_id} ---")
    
    profiles = [
        "Top-rated merchant (4.8/5 stars, 98% order accuracy, minimal complaints) - Excellent track record",
        "Good merchant (4.4/5 stars, 94% order accuracy, occasional packaging issues) - Generally reliable",
        "Average merchant (4.1/5 stars, 88% order accuracy, moderate complaint rate) - Needs improvement",
        "Problematic merchant (3.8/5 stars, 82% order accuracy, frequent quality issues) - Under performance review"
    ]
    
    return f"Merchant Profile: {random.choice(profiles)}"

def track_delivery_status(order_id: str) -> str:
    """Get real-time delivery tracking with detailed status information"""
    print(f"--- Tracking Order: {order_id} ---")
    
    # Generate realistic tracking scenarios
    tracking_scenarios = [
        {
            "status": "order_confirmed",
            "location": "Food Corner Restaurant",
            "estimated_time": "25 minutes",
            "details": "Order confirmed by restaurant. Currently being prepared.",
            "next_update": "Driver assignment in 10-15 minutes"
        },
        {
            "status": "preparing", 
            "location": "Food Corner Kitchen",
            "estimated_time": "20 minutes",
            "details": "Your food is being freshly prepared by the restaurant.",
            "next_update": "Driver will be assigned once preparation is complete"
        },
        {
            "status": "ready_for_pickup",
            "location": "Food Corner Restaurant", 
            "estimated_time": "15 minutes",
            "details": "Food is ready! Waiting for driver assignment.",
            "next_update": "Driver pickup in 5-10 minutes"
        },
        {
            "status": "driver_assigned",
            "location": "En route to restaurant",
            "estimated_time": "18 minutes", 
            "details": "Mike Wilson (Driver) has been assigned and is heading to pickup your order.",
            "next_update": "Pickup confirmation expected in 8-12 minutes"
        },
        {
            "status": "picked_up",
            "location": "0.8 km from your location",
            "estimated_time": "12 minutes",
            "details": "Driver Mike Wilson has picked up your order and is on the way to you!",
            "next_update": "Live tracking available, delivery in progress"
        },
        {
            "status": "nearby",
            "location": "200 meters from delivery address", 
            "estimated_time": "3 minutes",
            "details": "Your driver is very close! Please be ready to receive your order.",
            "next_update": "Delivery completion imminent"
        },
        {
            "status": "delayed_traffic",
            "location": "Stuck in traffic, 1.2 km away",
            "estimated_time": "25 minutes (updated)",
            "details": "Heavy traffic is causing delays. Driver is in slow-moving traffic but making progress.",
            "next_update": "Continuous updates as traffic clears"
        },
        {
            "status": "delayed_weather",
            "location": "Taking shelter, 0.5 km away", 
            "estimated_time": "20 minutes (weather delay)",
            "details": "Driver has temporarily stopped due to heavy rain for safety. Will resume delivery once safe.",
            "next_update": "Movement will resume when weather improves"
        }
    ]
    
    scenario = random.choice(tracking_scenarios)
    
    return f"""📍 **LIVE ORDER TRACKING - {order_id}**

🚗 **Current Status:** {scenario['status'].replace('_', ' ').title()}
📍 **Location:** {scenario['location']}
⏰ **Estimated Delivery:** {scenario['estimated_time']}

📋 **Details:** {scenario['details']}
🔄 **Next Update:** {scenario['next_update']}

👤 **Your Driver:** Mike Wilson (★4.6 rating)
📞 **Contact:** Available through app

💡 **What you can do:**
• Track live location in the app
• Contact driver if needed  
• Prepare to receive delivery"""

def analyze_gps_data(order_id: str) -> str:
    """Analyze GPS coordinates and route efficiency."""
    print(f"--- Analyzing GPS Data: {order_id} ---")
    
    return """GPS Analysis:
    • Route Efficiency: 94% optimal (standard city traffic)
    • Speed Analysis: Average 28 km/h (within normal range)
    • Stop Points: Merchant pickup (2 min) → Direct route → Customer location
    • Anomalies: None detected
    • Verification: GPS coordinates match reported delivery address"""

def check_weather_conditions(location_time: str) -> str:
    """Check weather conditions with enhanced context for delivery delays"""
    print(f"--- Checking Weather Context: {location_time} ---")
    
    # Simulate realistic weather conditions
    weather_scenarios = [
        {
            "condition": "Heavy Rainfall",
            "impact": "Severe delivery delays expected",
            "description": "Intense rainfall with 25mm/hour precipitation. Roads are waterlogged in several areas.",
            "delivery_impact": "30-45 minute delays typical",
            "safety_note": "Drivers taking extra caution for safety"
        },
        {
            "condition": "Thunderstorm Warning", 
            "impact": "Major service disruptions",
            "description": "Active thunderstorm with lightning. Many delivery partners temporarily sheltering.",
            "delivery_impact": "45-60 minute delays possible",
            "safety_note": "Safety protocols require drivers to seek shelter during lightning"
        },
        {
            "condition": "Light Rain",
            "impact": "Minor delivery delays",
            "description": "Light intermittent showers affecting traffic flow.",
            "delivery_impact": "10-15 minute delays",
            "safety_note": "Slower speeds for safety"
        },
        {
            "condition": "Clear Weather",
            "impact": "Normal delivery operations",
            "description": "Clear skies with good visibility.",
            "delivery_impact": "No weather-related delays",
            "safety_note": "Optimal delivery conditions"
        },
        {
            "condition": "Heavy Traffic + Rain",
            "impact": "Combined delays",
            "description": "Rain causing significant traffic congestion throughout the city.",
            "delivery_impact": "20-35 minute delays",
            "safety_note": "Delivery partners navigating carefully through congested areas"
        }
    ]
    
    # Select weather based on time of day and randomness
    current_hour = datetime.now().hour
    if 17 <= current_hour <= 20:  # Peak hours
        weather = random.choice(weather_scenarios[:3])  # More likely to have issues
    else:
        weather = random.choice(weather_scenarios)
    
    return f"""🌦️ WEATHER ANALYSIS - {location_time.upper()}:

**Current Conditions:** {weather['condition']}
**Impact Level:** {weather['impact']}

📊 **Detailed Report:**
• Weather: {weather['description']}
• Delivery Impact: {weather['delivery_impact']}
• Safety Consideration: {weather['safety_note']}

🚗 **Recommendation for Customer Service:**
{weather['condition']} is affecting delivery operations in your area. This provides context for any delays and shows our delivery partners are prioritizing safety while protecting food quality.

**Use this information to:**
• Explain delays with empathy and context
• Show customer that delays are weather-related, not service failures
• Demonstrate mature understanding of uncontrollable factors"""

def contact_driver(driver_message: str) -> str:
    """Send message or call driver for clarification."""
    driver_id, message = driver_message.split(',', 1) if ',' in driver_message else (driver_message, "Status update")
    print(f"--- Contacting Driver {driver_id}: {message} ---")
    
    responses = [
        "Driver responded: 'Customer not at delivery address, trying alternative contact'",
        "Driver confirmed: 'Order delivered to specified location, customer received items'",
        "Driver explained: 'Traffic jam caused delay, sent customer notification'",
        "Driver reported: 'Merchant had to remake order due to quality issue'"
    ]
    
    return f"Driver Communication: {random.choice(responses)}"

def contact_merchant(merchant_message: str) -> str:
    """Contact merchant about order issues."""
    merchant_id, message = merchant_message.split(',', 1) if ',' in merchant_message else (merchant_message, "Order inquiry")
    print(f"--- Contacting Merchant {merchant_id}: {message} ---")
    
    responses = [
        "Merchant confirmed: 'Order prepared correctly, packaged according to standards'",
        "Merchant admitted: 'Kitchen error occurred, willing to remake order at no charge'",
        "Merchant explained: 'Delay due to ingredient shortage, offered substitute items'",
        "Merchant investigating: 'Reviewing kitchen procedures, will provide feedback within 2 hours'"
    ]
    
    return f"Merchant Response: {random.choice(responses)}"

def verify_customer_identity(verification_request: str) -> str:
    """Verify customer identity for security purposes."""
    customer_id, method = verification_request.split(',', 1) if ',' in verification_request else (verification_request, "standard")
    print(f"--- Verifying Customer Identity: {customer_id} via {method} ---")
    
    return f"Identity Verification: Customer {customer_id} successfully verified via {method}. Security check passed."

def offer_compensation_voucher(voucher_details: str) -> str:
    """Offer voucher or credits as compensation."""
    try:
        customer_id, amount, voucher_type = voucher_details.split(',')
        print(f"--- Offering Voucher: {voucher_type} worth {amount} to {customer_id} ---")
        return f"Successfully issued {voucher_type} voucher worth ${amount} to customer {customer_id}. Valid for 30 days, applicable to future orders."
    except:
        return "Error: Please provide voucher details as customer_id,amount,voucher_type"

def issue_instant_refund(refund_details: str) -> str:
    """Issue instant refund with proper documentation."""
    try:
        customer_id, amount, reason = refund_details.split(',', 2)
        print(f"--- Processing Refund: ${amount} to {customer_id} for {reason} ---")
        return f"Instant refund of ${amount} processed for customer {customer_id}. Reason: {reason}. Funds will appear in 1-3 business days."
    except:
        return "Error: Please provide refund details as customer_id,amount,reason"

def exonerate_driver(driver_details: str) -> str:
    """Clear driver of fault with documentation."""
    driver_id, reason = driver_details.split(',', 1) if ',' in driver_details else (driver_details, "Evidence supports innocence")
    print(f"--- Exonerating Driver {driver_id}: {reason} ---")
    return f"Driver {driver_id} cleared of all fault. Reason: {reason}. No impact on performance record."

def log_merchant_packaging_feedback(feedback_details: str) -> str:
    """Log detailed merchant feedback for quality improvement."""
    try:
        merchant_id, feedback = feedback_details.split(',', 1)
        print(f"--- Logging Merchant Feedback: {merchant_id} ---")
        return f"Quality feedback logged for merchant {merchant_id}: '{feedback}'. Forwarded to merchant quality team for review and improvement action."
    except:
        return "Error: Please provide feedback as merchant_id,feedback_details"

def log_incident_report(incident_details: str) -> str:
    """Create comprehensive incident report."""
    try:
        incident_type, details, parties = incident_details.split(',', 2)
        print(f"--- Creating Incident Report: {incident_type} ---")
        return f"Incident report #{random.randint(10000,99999)} created. Type: {incident_type}. Details logged for analysis. Involved parties: {parties}. Report forwarded to quality assurance team."
    except:
        return "Error: Please provide incident details as incident_type,details,involved_parties"

def escalate_to_human(escalation_request: str) -> str:
    """Escalate complex cases to human agents."""
    try:
        reason, urgency, summary = escalation_request.split(',', 2)
        print(f"--- Escalating to Human Agent: {urgency} priority ---")
        return f"Case escalated to human agent. Priority: {urgency}. Reason: {reason}. Case summary provided. Expected response time: {'30 minutes' if urgency == 'high' else '2 hours' if urgency == 'medium' else '24 hours'}."
    except:
        return "Case escalated to human agent team for specialized handling."

def check_traffic(location: str, route: str = "") -> str:
    """Check current traffic conditions for a specific location and route."""
    print(f"--- Checking Traffic Conditions: {location} ---")
    
    # Simulate traffic conditions
    traffic_conditions = [
        f"Traffic Status for {location}: Light traffic, normal flow. Expected delivery time on schedule.",
        f"Traffic Status for {location}: Moderate congestion detected. +5-8 minutes delay expected.",
        f"Traffic Status for {location}: Heavy traffic due to construction. +15-20 minutes delay likely.",
        f"Traffic Status for {location}: Severe congestion - accident reported. +25-30 minutes delay. Rerouting recommended.",
        f"Traffic Status for {location}: Road closure in effect. Alternative route required. +10-15 minutes delay."
    ]
    
    route_info = f" Route: {route}" if route else ""
    
    return f"{random.choice(traffic_conditions)}{route_info}\n\nRecommendation: {'Consider alternative routes' if 'Heavy' in traffic_conditions[-1] or 'Severe' in traffic_conditions[-1] else 'Current route optimal'}"

def get_merchant_status(merchant_id: str) -> str:
    """Get current operational status of a specific merchant."""
    print(f"--- Checking Merchant Status: {merchant_id} ---")
    
    if SANDBOX_AVAILABLE:
        # Try to get merchant from sandbox
        try:
            merchant_data = sandbox_db.get_merchant(merchant_id)
            if merchant_data:
                prep_time = random.choice([8, 12, 15, 18, 25])
                queue_length = random.choice([2, 5, 8, 12, 15])
                
                return f"""Merchant Status - {merchant_data['name']}:
• Operational Status: OPEN
• Current Queue: {queue_length} orders
• Average Prep Time: {prep_time} minutes
• Quality Rating: {merchant_data['rating']}/5.0
• Cuisine: {merchant_data['cuisine_type']}
• Location: {merchant_data['address']}
• Special Notes: {'Rush hour - slight delays expected' if queue_length > 10 else 'Normal operations'}"""
        except:
            pass
    
    # Fallback status options
    statuses = [
        f"Merchant {merchant_id}: OPEN - Normal operations, 8-12 min prep time, 3 orders in queue",
        f"Merchant {merchant_id}: BUSY - High demand, 15-20 min prep time, 8 orders in queue", 
        f"Merchant {merchant_id}: SLOW - Kitchen delays, 20-25 min prep time, 12 orders in queue",
        f"Merchant {merchant_id}: TEMPORARILY CLOSED - Kitchen maintenance, reopening in 30 minutes",
        f"Merchant {merchant_id}: LIMITED MENU - Some items unavailable, normal prep times"
    ]
    
    return random.choice(statuses)

def reroute_driver(driver_id: str, new_route: str) -> str:
    """Reroute driver to avoid traffic or optimize delivery path."""
    print(f"--- Rerouting Driver {driver_id}: {new_route} ---")
    
    # Simulate route optimization
    original_eta = random.randint(12, 25)
    optimized_eta = max(8, original_eta - random.randint(3, 8))
    distance_saved = round(random.uniform(0.5, 2.3), 1)
    
    return f"""Driver Rerouting Successful:
• Driver ID: {driver_id}
• New Route: {new_route}
• Original ETA: {original_eta} minutes
• Optimized ETA: {optimized_eta} minutes
• Time Saved: {original_eta - optimized_eta} minutes
• Distance Saved: {distance_saved} km
• Route Status: Driver notified and navigation updated
• Customer Notification: Auto-sent with updated delivery time"""

def get_nearby_merchants(location: str, cuisine_type: str = "") -> str:
    """Find nearby merchants based on location and cuisine preference."""
    print(f"--- Finding Nearby Merchants: {location}, Cuisine: {cuisine_type} ---")
    
    if SANDBOX_AVAILABLE:
        try:
            # Get merchants from sandbox
            merchants = []
            for merchant in sandbox_db.merchants.values():
                if not cuisine_type or cuisine_type.lower() in merchant['cuisine_type'].lower():
                    distance = round(random.uniform(0.3, 3.5), 1)
                    eta = random.randint(15, 35)
                    merchants.append(f"• {merchant['name']} - {merchant['cuisine_type']} ({distance}km, ~{eta}min delivery)")
            
            if merchants:
                return f"Nearby Merchants in {location}:\n" + "\n".join(merchants[:5])
        except:
            pass
    
    # Fallback merchant suggestions
    cuisine_filter = f" ({cuisine_type})" if cuisine_type else ""
    
    sample_merchants = [
        f"• Spice Garden{cuisine_filter} - 0.8km away, ~20min delivery, 4.5★",
        f"• Quick Bites Express{cuisine_filter} - 1.2km away, ~15min delivery, 4.3★", 
        f"• Golden Fork Restaurant{cuisine_filter} - 1.5km away, ~25min delivery, 4.7★",
        f"• Street Food Corner{cuisine_filter} - 0.5km away, ~12min delivery, 4.2★",
        f"• Fusion Kitchen{cuisine_filter} - 2.1km away, ~30min delivery, 4.6★"
    ]
    
    return f"Nearby Merchants in {location}:\n" + "\n".join(random.sample(sample_merchants, min(4, len(sample_merchants))))

def initiate_mediation_flow(order_id: str) -> str:
    """Start mediation process between customer, merchant, and driver for complex disputes."""
    print(f"--- Initiating Mediation Flow: {order_id} ---")
    
    if SANDBOX_AVAILABLE:
        try:
            order_data = sandbox_db.get_order(order_id)
            if order_data:
                customer_id = order_data['customer_id'] 
                merchant_id = order_data['merchant_id']
                driver_id = order_data.get('driver_id', 'TBD')
                
                return f"""Mediation Process Initiated for Order {order_id}:

📋 CASE DETAILS:
• Customer: {customer_id}
• Merchant: {merchant_id} 
• Driver: {driver_id}
• Order Value: ₹{order_data['total_amount']}
• Issue Type: Complex dispute requiring mediation

🔄 MEDIATION WORKFLOW:
1. ✅ All parties notified
2. ⏳ Evidence collection (24hr window)
3. ⏳ Review by mediation specialist
4. ⏳ Resolution conference (if needed)
5. ⏳ Final decision & compensation

📞 CONTACT ASSIGNED:
• Mediation Specialist: Sarah Chen
• Case Number: MED-{random.randint(1000,9999)}
• Expected Resolution: 48-72 hours
• All parties will receive updates via SMS/email"""
        except:
            pass
    
    return f"""Mediation Flow Initiated for Order {order_id}:
• Case escalated to mediation team
• All parties (customer, merchant, driver) will be contacted
• Evidence review period: 24 hours
• Mediation specialist assigned
• Expected resolution: 48-72 hours
• Case reference: MED-{random.randint(1000,9999)}"""

def find_nearby_locker(location: str) -> str:
    """Find nearby Grab lockers for self-pickup or alternative delivery."""
    print(f"--- Finding Nearby Lockers: {location} ---")
    
    # Simulate locker locations
    locker_options = [
        f"📍 GrabLocker @ Central Mall, {location}",
        f"📍 GrabLocker @ Metro Station Plaza, {location}", 
        f"📍 GrabLocker @ Office Complex Hub, {location}",
        f"📍 GrabLocker @ University Campus, {location}",
        f"📍 GrabLocker @ Residential Tower, {location}"
    ]
    
    selected_lockers = random.sample(locker_options, min(3, len(locker_options)))
    
    locker_details = []
    for i, locker in enumerate(selected_lockers):
        distance = round(random.uniform(0.2, 1.8), 1)
        available_slots = random.randint(3, 15)
        walk_time = random.randint(2, 8)
        
        locker_details.append(f"{locker}\n  • Distance: {distance}km ({walk_time}min walk)\n  • Available Slots: {available_slots}\n  • Operating Hours: 6:00 AM - 11:00 PM")
    
    return f"""Nearby GrabLockers in {location}:

{chr(10).join(locker_details)}

💡 LOCKER BENEFITS:
• No delivery fee for locker pickup
• 24-hour pickup window
• SMS notification when order arrives
• Contactless pickup with QR code
• Secure temperature-controlled storage

Would you like me to redirect your order to one of these lockers?"""

def analyze_image_evidence(image_context: str) -> str:
    """Analyze image evidence provided by customer for complaint investigation."""
    print(f"--- Analyzing Image Evidence: {image_context} ---")
    
    # Extract image analysis information if provided
    if "Image Evidence:" in image_context:
        evidence_parts = image_context.split("Evidence Details:")
        description = evidence_parts[0].replace("Image Evidence:", "").strip()
        details = evidence_parts[1].strip() if len(evidence_parts) > 1 else ""
        
        return f"""🔍 IMAGE EVIDENCE ANALYSIS COMPLETE:

📸 VISUAL CONFIRMATION: {description}

🔬 EXTRACTED EVIDENCE:
{details}

✅ EVIDENCE ASSESSMENT:
• Authenticity: High confidence
• Relevance: Directly supports customer complaint
• Clarity: Clear evidence of service failure
• Impact: Justifies immediate resolution

🎯 RECOMMENDED ACTION:
Based on photographic evidence, customer complaint is validated. Proceed with:
1. Full compensation as justified by visual evidence
2. Quality assurance follow-up with relevant service provider
3. Process improvement to prevent similar incidents

The image evidence strongly supports the customer's claim and warrants immediate resolution."""
    
    # Handle general image context
    return f"""🔍 IMAGE EVIDENCE REVIEW:

📸 Evidence Provided: {image_context}

✅ EVIDENCE STATUS:
• Customer has provided visual documentation
• Evidence supports their complaint description
• Documentation aids in fair resolution
• Validates customer's experience

🎯 RESOLUTION APPROACH:
With supporting visual evidence, we can proceed with confident resolution:
1. Evidence confirms service issue occurred
2. Visual proof supports compensation decision
3. Documentation helps prevent future incidents

The provided image evidence strengthens the case for immediate customer compensation."""

def orchestrate_resolution_plan(issue_details: str) -> str:
    """Create and execute a comprehensive multi-step resolution plan with proactive problem detection."""
    print(f"--- Orchestrating Resolution Plan: {issue_details} ---")
    
    details_lower = issue_details.lower()
    
    # Advanced issue classification with severity scoring
    severity_score = 0
    issue_type = "general"
    emotional_indicators = []
    
    # Critical issues (100 points)
    if any(critical in details_lower for critical in ["spilled", "poisoned", "allergic", "sick", "emergency"]):
        severity_score = 100
        issue_type = "critical_failure"
    
    # High severity (75 points)
    elif any(high in details_lower for high in ["wrong order", "missing", "damaged", "terrible", "awful", "disgusted"]):
        severity_score = 75
        issue_type = "major_service_failure"
    
    # Medium severity (50 points)
    elif any(medium in details_lower for medium in ["cold", "late", "delayed", "poor quality", "disappointed"]):
        severity_score = 50
        issue_type = "quality_issue"
    
    # Low severity (25 points)
    else:
        severity_score = 25
        issue_type = "minor_concern"
    
    # Detect emotional indicators
    if any(anger in details_lower for anger in ["angry", "furious", "outraged", "disgusted"]):
        emotional_indicators.append("high_anger")
        severity_score += 15
    elif any(frustration in details_lower for frustration in ["frustrated", "annoyed", "disappointed"]):
        emotional_indicators.append("frustration")
        severity_score += 10
    
    # Detect repeat customer signals
    if any(repeat in details_lower for repeat in ["again", "always", "every time", "repeatedly"]):
        emotional_indicators.append("repeat_issue")
        severity_score += 20
    
    # Create dynamic resolution plan
    plan_steps = []
    compensation_level = "standard"
    
    if severity_score >= 90:
        compensation_level = "premium_plus"
        plan_steps = [
            "🚨 IMMEDIATE ESCALATION: Critical service failure detected",
            "💳 Full refund + 200% compensation credit",
            "🎁 Premium customer care package",
            "📞 Personal follow-up call within 2 hours",
            "🛡️ Quality assurance investigation",
            "📊 Executive team notification"
        ]
    elif severity_score >= 70:
        compensation_level = "premium"
        plan_steps = [
            "⚡ HIGH PRIORITY: Major service failure acknowledged", 
            "💳 Full refund + 150% compensation credit",
            "🚀 Immediate reorder (if applicable)",
            "📧 Personal apology from management",
            "🔍 Root cause analysis",
            "📈 Process improvement review"
        ]
    elif severity_score >= 45:
        compensation_level = "enhanced"
        plan_steps = [
            "🎯 STANDARD RESOLUTION: Quality issue identified",
            "💳 Full refund + 100% compensation credit", 
            "🎁 Future order discount voucher",
            "📝 Merchant feedback submission",
            "📊 Quality monitoring alert"
        ]
    else:
        compensation_level = "basic"
        plan_steps = [
            "✅ QUICK RESOLUTION: Minor concern addressed",
            "💳 Partial refund or service credit",
            "🎫 Goodwill voucher",
            "📋 Standard feedback logging"
        ]
    
    emotional_response = ""
    if "high_anger" in emotional_indicators:
        emotional_response = "\n🤝 EMOTIONAL SUPPORT: Extra empathy protocols activated - customer anger management approach"
    elif "frustration" in emotional_indicators:
        emotional_response = "\n😊 CUSTOMER CARE: Frustration acknowledged - enhanced communication mode"
    
    if "repeat_issue" in emotional_indicators:
        emotional_response += "\n🔄 REPEAT CUSTOMER ALERT: Pattern detected - priority handling + retention measures"
    
    return f"""🧠 ADVANCED RESOLUTION ORCHESTRATION:

🎯 ISSUE CLASSIFICATION:
• Severity Score: {severity_score}/100
• Issue Type: {issue_type.replace('_', ' ').title()}
• Compensation Level: {compensation_level.replace('_', ' ').title()}
• Emotional Indicators: {', '.join(emotional_indicators) if emotional_indicators else 'None detected'}

📋 MULTI-STEP EXECUTION PLAN:
{chr(10).join([f'{i+1}. {step}' for i, step in enumerate(plan_steps)])}

{emotional_response}

🚀 PROACTIVE MEASURES:
• Real-time merchant notification
• Driver performance review (if applicable)  
• Customer satisfaction follow-up scheduled
• Quality improvement recommendation generated

✅ EXECUTION STATUS: Plan activated - all steps proceeding simultaneously for fastest resolution."""


def gather_compensation_details(customer_query: str) -> str:
    """
    Gather order value and customer expectations before negotiating compensation.
    Business-focused approach to understand customer needs and order context.
    """
    print(f"--- Gathering Compensation Details for: {customer_query} ---")
    
    # Extract order value if mentioned
    order_value = None
    if "₹" in customer_query or "rs" in customer_query.lower() or "rupees" in customer_query.lower():
        import re
        amount_match = re.search(r'₹(\d+)|rs\s*(\d+)|(\d+)\s*rupees', customer_query.lower())
        if amount_match:
            order_value = int(amount_match.group(1) or amount_match.group(2) or amount_match.group(3))
    
    # Default order value for simulation
    if not order_value:
        order_value = random.choice([250, 350, 450, 550, 650, 750, 850, 950])
    
    # Determine issue type for context
    issue_severity = "medium"
    if any(word in customer_query.lower() for word in ["completely wrong", "terrible", "disgusting", "awful", "horrible"]):
        issue_severity = "high"
    elif any(word in customer_query.lower() for word in ["slightly", "minor", "small", "bit"]):
        issue_severity = "low"
    
    return f"""💼 COMPENSATION ASSESSMENT REQUIRED:

📊 ORDER CONTEXT:
• Estimated Order Value: ₹{order_value}
• Issue Severity: {issue_severity.title()}
• Customer Tone: {'Frustrated' if issue_severity == 'high' else 'Disappointed' if issue_severity == 'medium' else 'Mild concern'}

❓ INFORMATION NEEDED FROM CUSTOMER:
To provide fair compensation, I need to understand:

1. "Could you confirm your total order value?"
2. "What specific items were affected?"
3. "What would make this situation right for you?"
4. "Would you prefer a refund or Grab credits for future orders?"

💡 BUSINESS CONTEXT:
• Standard compensation: 30-60% of affected items
• Delivery costs: ₹40-60 per order
• Customer retention value: High priority
• Company policy: Fair but sustainable compensation

⚡ NEXT STEP: Use negotiate_fair_compensation() after gathering customer preferences."""


def negotiate_fair_compensation(order_details: str) -> str:
    """
    Negotiate fair compensation that balances customer satisfaction with business interests.
    Uses dynamic pricing based on issue type, order value, and business constraints.
    """
    print(f"--- Negotiating Fair Compensation: {order_details} ---")
    
    # Extract order value from details
    order_value = 500  # Default
    if "₹" in order_details:
        import re
        match = re.search(r'₹(\d+)', order_details)
        if match:
            order_value = int(match.group(1))
    
    # Determine issue type and calculate base compensation (CAPPED AT 50%)
    issue_type = "general"
    base_percentage = 25  # More conservative starting point
    
    if any(word in order_details.lower() for word in ["wrong", "incorrect", "different"]):
        issue_type = "wrong_order"
        base_percentage = 30
    elif any(word in order_details.lower() for word in ["spilled", "damaged", "cold", "soggy"]):
        issue_type = "quality_issue"
        base_percentage = 40
    elif any(word in order_details.lower() for word in ["late", "delay", "waiting"]):
        issue_type = "delivery_delay"
        base_percentage = 15
    elif any(word in order_details.lower() for word in ["missing", "incomplete"]):
        issue_type = "missing_items"
        base_percentage = 35
    
    # Calculate compensation with MAXIMUM 50% CAP
    base_compensation = int(order_value * base_percentage / 100)
    delivery_cost = random.choice([45, 50, 55, 60])  # Average delivery cost
    goodwill_voucher = random.choice([30, 40, 50])  # Smaller goodwill gesture
    
    # Create negotiation tiers - MAXIMUM 50% of order value
    tier_1_offer = base_compensation
    tier_2_offer = min(base_compensation + 30, int(order_value * 0.4))  # Max 40% in tier 2
    tier_3_offer = min(int(order_value * 0.5), base_compensation + 60)  # HARD CAP AT 50%
    
    customer_satisfaction_score = random.choice([75, 80, 85, 90])
    
    return f"""🤝 CONSERVATIVE COMPENSATION NEGOTIATION:

📋 ASSESSMENT SUMMARY:
• Order Value: ₹{order_value}
• Issue Type: {issue_type.replace('_', ' ').title()}
• Affected Amount: ~₹{base_compensation} worth of items
• Our Delivery Cost: ₹{delivery_cost}

💼 CONSERVATIVE BUSINESS OFFER (MAX 50% OF ORDER VALUE):

🎯 PRIMARY OFFER (Starting Point):
• Cash Refund: ₹{tier_1_offer}
• Goodwill Credit: ₹{goodwill_voucher}
• Total Value: ₹{tier_1_offer + goodwill_voucher}

📈 ESCALATION TIERS (if customer requests more):
• Tier 2: ₹{tier_2_offer} refund + ₹{goodwill_voucher} credit
• Tier 3: ₹{tier_3_offer} refund + ₹{goodwill_voucher} credit (ABSOLUTE MAXIMUM - 50% CAP)

💡 NEGOTIATION TALKING POINTS:
✅ "This covers the affected portion of your order plus inconvenience"
✅ "We're also absorbing our ₹{delivery_cost} delivery cost as goodwill"
✅ "Our policy caps compensation at 50% of order value for fairness to all customers"
✅ "This reflects both your loss and our business sustainability constraints"

❌ IMPORTANT CONSTRAINTS:
• "Maximum compensation is 50% of order value as per company policy"
• "This helps us maintain fair service for all customers"
• "If unsatisfied with this maximum offer, I can escalate to a human agent"

🚨 ESCALATION TRIGGER: If customer rejects 50% offer → escalate to human
🎖️ CUSTOMER RETENTION PRIORITY: {customer_satisfaction_score}% satisfaction target
🚦 APPROVAL STATUS: Pre-approved up to ₹{tier_3_offer} (50% maximum)"""


def explain_business_compensation_policy(issue_type: str) -> str:
    """
    Explain Grab's compensation philosophy to help customers understand business constraints
    while demonstrating empathy and fairness.
    """
    print(f"--- Explaining Compensation Policy for: {issue_type} ---")
    
    policies = {
        "wrong_order": {
            "coverage": "45-60% of order value",
            "reasoning": "Covers unusable items while considering preparation and delivery costs already invested",
            "typical_range": "₹200-400 for average orders"
        },
        "quality_issue": {
            "coverage": "50-70% of affected items",
            "reasoning": "Higher coverage for quality failures as this impacts trust and health",
            "typical_range": "₹150-350 depending on severity"
        },
        "delivery_delay": {
            "coverage": "₹50-150 credits",
            "reasoning": "Food still delivered and usable, compensation for time inconvenience",
            "typical_range": "₹75-125 for delays over 30 minutes"
        },
        "missing_items": {
            "coverage": "60-80% of missing item value",
            "reasoning": "Full item replacement cost plus inconvenience, as item not received",
            "typical_range": "₹100-300 based on missing items"
        }
    }
    
    policy = policies.get(issue_type, policies["wrong_order"])
    
    return f"""📋 GRAB'S FAIR COMPENSATION PHILOSOPHY:

🎯 FOR {issue_type.replace('_', ' ').upper()} ISSUES:
• Coverage Range: {policy['coverage']}
• Business Reasoning: {policy['reasoning']}
• Typical Amounts: {policy['typical_range']}

💼 WHY THESE AMOUNTS:
✅ Covers your direct loss and inconvenience
✅ Accounts for costs we've already invested (delivery, preparation, platform fees)
✅ Ensures sustainable service quality for all customers
✅ Balances fairness with business viability

🤝 OUR COMMITMENT:
• You receive value that makes the situation right
• We maintain quality service through sustainable practices
• Fair treatment for both customer and business interests
• Long-term relationship over short-term maximum payouts

💡 ADDITIONAL VALUE:
• Grab credits often provide 10-15% bonus value
• Priority customer status for future issues
• Quality monitoring to prevent repeat problems
• Direct feedback to merchants for improvement

🎖️ RESULT: Satisfied customers + sustainable business = better service for everyone"""


def calculate_dynamic_refund_amount(order_value: int, issue_type: str, customer_expectation: str = "reasonable") -> str:
    """
    Calculate contextual refund amounts based on order value, issue severity, and business logic.
    Provides justification for the amount to help with customer negotiation.
    """
    print(f"--- Calculating Dynamic Refund: ₹{order_value} order, {issue_type} ---")
    
    # Base compensation percentages by issue type (CAPPED AT 50%)
    compensation_matrix = {
        "wrong_order": {"min": 25, "max": 40},
        "quality_issue": {"min": 30, "max": 50},
        "delivery_delay": {"min": 10, "max": 25},
        "missing_items": {"min": 35, "max": 50},
        "spilled_food": {"min": 35, "max": 50},
        "cold_food": {"min": 20, "max": 35},
        "damaged_packaging": {"min": 15, "max": 30}
    }
    
    # Get compensation range
    comp_range = compensation_matrix.get(issue_type, {"min": 40, "max": 60})
    
    # Adjust based on customer expectation but CAP AT 50%
    if "full refund" in customer_expectation.lower() or "complete" in customer_expectation.lower():
        percentage = min(comp_range["max"], 50)  # Never exceed 50%
        tier = "maximum (50% cap)"
    elif "partial" in customer_expectation.lower() or "some" in customer_expectation.lower():
        percentage = comp_range["min"]
        tier = "minimal"
    else:
        percentage = (comp_range["min"] + min(comp_range["max"], 50)) // 2
        tier = "standard"
    
    # Calculate amounts
    refund_amount = int(order_value * percentage / 100)
    goodwill_credit = random.choice([50, 75, 100])
    delivery_cost = random.choice([45, 50, 55])
    
    # Business cost analysis
    total_grab_cost = delivery_cost + random.choice([25, 30, 35])  # Platform costs
    net_business_impact = refund_amount + goodwill_credit - (order_value - total_grab_cost)
    
    return f"""💰 DYNAMIC REFUND CALCULATION:

📊 ORDER ANALYSIS:
• Order Value: ₹{order_value}
• Issue Type: {issue_type.replace('_', ' ').title()}
• Compensation Tier: {tier.title()}
• Coverage Percentage: {percentage}%

💳 RECOMMENDED COMPENSATION:
• Primary Refund: ₹{refund_amount}
• Goodwill Credit: ₹{goodwill_credit}
• Total Customer Value: ₹{refund_amount + goodwill_credit}

📈 BUSINESS IMPACT ANALYSIS:
• Our Delivery Investment: ₹{delivery_cost}
• Platform & Processing Costs: ₹{total_grab_cost}
• Net Business Impact: ₹{abs(net_business_impact)} {'loss' if net_business_impact > 0 else 'manageable cost'}

🎯 NEGOTIATION RATIONALE:
✅ "This ₹{refund_amount} covers the unusable portion of your order"
✅ "The ₹{goodwill_credit} credit acknowledges your inconvenience"  
✅ "We're absorbing our ₹{total_grab_cost} operational costs"
✅ "Total value of ₹{refund_amount + goodwill_credit} shows our commitment to making this right"

🚦 APPROVAL STATUS: {"Pre-approved" if refund_amount <= order_value * 0.5 else "Exceeds 50% policy - requires escalation"}
💡 CUSTOMER SATISFACTION TARGET: {random.choice([85, 90, 95])}% resolution confidence"""


def request_visual_evidence(issue_description: str) -> str:
    """
    Request customer to provide photo evidence for better assessment
    """
    print(f"--- Requesting Visual Evidence: {issue_description} ---")
    
    # Determine appropriate evidence request based on issue
    issue_lower = issue_description.lower()
    
    if any(word in issue_lower for word in ["spill", "damage", "mess", "leak"]):
        evidence_type = "spilled or damaged food"
        specific_request = "Could you please share a photo showing the spilled/damaged food? This will help me understand exactly what happened and ensure we address this properly."
        
    elif any(word in issue_lower for word in ["wrong", "different", "mistake"]):
        evidence_type = "wrong order items"
        specific_request = "Could you please take a photo of what you received versus what you ordered? This visual evidence will help me verify the mix-up and arrange the correct resolution."
        
    elif any(word in issue_lower for word in ["packaging", "broken", "container"]):
        evidence_type = "packaging condition"
        specific_request = "Could you please share a photo of the packaging/container issue? This helps us identify if this is a restaurant packaging problem or delivery handling issue."
        
    elif any(word in issue_lower for word in ["quality", "bad", "terrible", "awful"]):
        evidence_type = "food quality issue"
        specific_request = "Could you please take a photo showing the quality issue with the food? Visual evidence helps us provide accurate feedback to the restaurant."
        
    else:
        evidence_type = "order issue"
        specific_request = "Could you please share a photo of the issue you're experiencing? Visual evidence helps me understand the situation better."
    
    return f"""📸 **VISUAL EVIDENCE REQUEST**

Thank you for bringing this to our attention. To ensure I provide you with the most appropriate resolution, I'd like to gather some visual evidence.

🎯 **Evidence Needed:** Photo of {evidence_type}

📱 **How to submit:**
{specific_request}

You can upload the image using the attachment button in this chat.

💡 **Why we need this:**
• Visual evidence helps us understand exactly what went wrong
• Enables accurate assessment for fair resolution  
• Helps us provide feedback to restaurants/delivery partners for improvement
• Ensures we address your specific situation appropriately

⏰ **Next Steps:** Once I receive your photo, I'll immediately review the evidence and provide you with appropriate options for resolution.

Your feedback is valuable in helping us maintain service quality!"""


def log_customer_feedback(feedback_details: str, evidence_provided: str = "none") -> str:
    """
    Log customer feedback without admitting fault - position as valuable improvement data
    """
    print(f"--- Logging Customer Feedback: {feedback_details} ---")
    
    # Generate a feedback reference number
    feedback_id = f"FB{random.randint(10000, 99999)}"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Determine feedback category
    details_lower = feedback_details.lower()
    category = "General"
    
    if any(word in details_lower for word in ["spill", "damage", "mess"]):
        category = "Delivery Handling"
    elif any(word in details_lower for word in ["wrong", "different", "mistake"]):
        category = "Order Accuracy"
    elif any(word in details_lower for word in ["packaging", "container"]):
        category = "Packaging Quality"
    elif any(word in details_lower for word in ["quality", "food", "taste"]):
        category = "Food Quality"
    elif any(word in details_lower for word in ["late", "delay", "time"]):
        category = "Delivery Timeliness"
    
    return f"""📋 **FEEDBACK LOGGED SUCCESSFULLY**

✅ **Feedback Reference:** {feedback_id}
📅 **Logged At:** {current_time}
🏷️ **Category:** {category}
📸 **Evidence:** {"Photo evidence attached" if evidence_provided != "none" else "Description provided"}

🎯 **Your Feedback Summary:**
"{feedback_details[:100]}..."

💡 **Impact of Your Feedback:**
• This information helps us identify improvement opportunities
• Quality control team will review for service enhancement
• Restaurant partners receive quality feedback for improvement
• Delivery processes will be evaluated based on your input

📊 **What Happens Next:**
• Your feedback is valuable data for our operations team
• We use this information to enhance service quality
• Relevant teams will be notified for process improvements
• Your experience contributes to better service for all customers

🙏 **Thank You for Your Input:**
Customer feedback like yours is essential for maintaining high service standards. Every report helps us serve you and other customers better.

*Your feedback has been recorded and will be used for service improvement purposes.*"""


def offer_goodwill_voucher(issue_type: str, customer_satisfaction_level: str = "dissatisfied") -> str:
    """
    Offer conservative goodwill vouchers (70-90%) only for extremely dissatisfied customers
    """
    print(f"--- Offering Goodwill Voucher: {issue_type}, satisfaction: {customer_satisfaction_level} ---")
    
    # Determine order value (simulated)
    order_value = random.choice([200, 300, 400, 500, 600, 700, 800])
    
    # Conservative voucher amounts based on satisfaction level
    if customer_satisfaction_level.lower() in ["extremely dissatisfied", "very upset", "angry"]:
        voucher_percentage = 70
        escalation_percentage = 90
    elif customer_satisfaction_level.lower() in ["dissatisfied", "unhappy"]:
        voucher_percentage = 50
        escalation_percentage = 70
    else:
        voucher_percentage = 30
        escalation_percentage = 50
    
    initial_voucher = int(order_value * voucher_percentage / 100)
    max_voucher = int(order_value * escalation_percentage / 100)
    
    # Generate voucher code
    voucher_code = f"GOODWILL{random.randint(1000, 9999)}"
    expiry_date = (datetime.now() + timedelta(days=30)).strftime("%d %B %Y")
    
    return f"""🎁 **GOODWILL GESTURE OFFERED**

I truly appreciate your patience and your valuable feedback. As a token of our commitment to service improvement, I'd like to offer you a goodwill voucher.

💳 **Voucher Details:**
• **Amount:** ₹{initial_voucher} Grab Credit
• **Code:** {voucher_code}
• **Valid Until:** {expiry_date}
• **Usage:** Any restaurant or delivery on Grab

✨ **This Voucher Represents:**
• Our appreciation for your feedback
• Commitment to better service quality
• Goodwill gesture for the inconvenience
• Investment in your continued trust

🎯 **Not a Refund - It's a Goodwill Gesture:**
This isn't compensation for fault - it's our way of saying thank you for helping us improve and showing we value your continued partnership with Grab.

💡 **How to Use:**
• Voucher will be added to your account within 5 minutes
• Use it on your next order automatically
• No minimum order requirement
• Stackable with other promotions

*If this gesture doesn't feel adequate for your experience, I can escalate this to our customer care team for additional review. Would you like me to connect you with a customer care officer?*

**Maximum possible goodwill voucher: ₹{max_voucher} if situation warrants**"""


def escalate_to_customer_care_officer(escalation_reason: str, customer_issue: str) -> str:
    """
    Escalate to human customer care officer with proper handoff
    """
    print(f"--- Escalating to Customer Care Officer: {escalation_reason} ---")
    
    # Generate escalation details
    escalation_id = f"ESC{random.randint(10000, 99999)}"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Simulated customer care officer (will add to sandbox later)
    care_officers = [
        {"name": "Sarah Chen", "id": "CO001", "specialization": "Delivery Issues", "rating": 4.8},
        {"name": "Rajesh Kumar", "id": "CO002", "specialization": "Food Quality", "rating": 4.9},
        {"name": "Maria Santos", "id": "CO003", "specialization": "Order Disputes", "rating": 4.7},
        {"name": "David Johnson", "id": "CO004", "specialization": "Customer Relations", "rating": 4.8}
    ]
    
    assigned_officer = random.choice(care_officers)
    estimated_wait = random.choice([3, 5, 7, 10])
    
    return f"""👤 **ESCALATION TO CUSTOMER CARE OFFICER**

I understand your concerns and want to ensure you receive the attention this matter deserves. I'm connecting you with one of our customer care specialists.

🎯 **Escalation Details:**
• **Reference ID:** {escalation_id}
• **Escalated At:** {current_time}
• **Reason:** {escalation_reason}

👨‍💼 **Your Assigned Officer:**
• **Name:** {assigned_officer['name']}
• **ID:** {assigned_officer['id']}
• **Specialization:** {assigned_officer['specialization']}
• **Customer Rating:** {assigned_officer['rating']}⭐

⏰ **Connection Details:**
• **Estimated Wait Time:** {estimated_wait} minutes
• **Contact Method:** Live chat transfer
• **Priority Level:** High (Escalated from AI)

📋 **Information Being Transferred:**
• Complete conversation history
• Issue details and evidence provided
• Previous resolution attempts
• Customer satisfaction concerns

💡 **What to Expect:**
• {assigned_officer['name']} has authority for enhanced resolutions
• Can approve additional goodwill measures if warranted
• Will provide personalized attention to your specific situation
• Has access to supervisor-level tools and options

🚀 **Preparing Transfer...**
*Please hold while I connect you with {assigned_officer['name']}. Your conversation history and case details are being transferred now.*

**Note:** {assigned_officer['name']} will be with you shortly and has full context of your situation."""


def escalate_compensation_dissatisfaction(customer_complaint: str, attempted_compensation: str = "50% of order value") -> str:
    """
    Handle escalation when customer is dissatisfied with maximum 50% compensation offer.
    Escalates to human agent with full context.
    """
    print(f"--- Escalating Compensation Dissatisfaction: {customer_complaint} ---")
    
    # Generate escalation reference number
    escalation_id = f"ESC_{random.randint(10000, 99999)}"
    
    # Determine escalation reason
    complaint_lower = customer_complaint.lower()
    escalation_reason = "General dissatisfaction"
    
    if any(word in complaint_lower for word in ["not enough", "more money", "full refund", "complete refund"]):
        escalation_reason = "Requesting compensation above 50% policy limit"
    elif any(word in complaint_lower for word in ["unfair", "ridiculous", "terrible", "awful"]):
        escalation_reason = "Customer expressing strong dissatisfaction with policy"
    elif any(word in complaint_lower for word in ["manager", "supervisor", "human", "person"]):
        escalation_reason = "Customer specifically requesting human intervention"
    elif any(word in complaint_lower for word in ["cancel", "never again", "complaint", "report"]):
        escalation_reason = "Customer threatening to escalate beyond Grab"
    
    return f"""🚨 ESCALATION TO HUMAN AGENT INITIATED

📋 ESCALATION SUMMARY:
• Escalation ID: {escalation_id}
• Reason: {escalation_reason}
• Max Compensation Offered: {attempted_compensation}
• Customer Response: {customer_complaint}

👤 HUMAN AGENT ASSIGNMENT:
• Queue: Customer Service Specialists
• Priority: High (Compensation Dispute)
• Estimated Wait Time: 3-5 minutes
• Agent Type: Senior Customer Care Officer

📝 CONTEXT PROVIDED TO AGENT:
• Customer has been offered maximum policy compensation (50% of order value)
• Customer is dissatisfied with this amount
• All standard compensation procedures have been followed
• Customer requires human judgment for resolution

💬 CUSTOMER MESSAGE:
"I understand you're not satisfied with our maximum compensation offer of {attempted_compensation}. I'm now connecting you with one of our senior customer care officers who has additional authority to review your case.

Your escalation ID is {escalation_id}. The specialist will have full context of our conversation and can explore additional options that may be available.

Please hold while I transfer you - estimated wait time is 3-5 minutes."

🎯 AGENT INSTRUCTIONS:
• Review full conversation history
• Customer has rejected maximum standard compensation
• Explore goodwill gestures beyond standard policy if appropriate
• Focus on customer retention and satisfaction
• Document final resolution for policy review

⚡ STATUS: Transfer in progress..."""
