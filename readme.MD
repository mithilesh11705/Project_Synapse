# Grab Customer Service AI Agent 🤖

An intelligent customer service automation system built for Grab's food delivery platform, featuring evidence-based complaint resolution, business-conservative compensation management, and seamless human escalation capabilities.

## 🌟 Overview

This project implements a sophisticated AI-powered customer service agent that revolutionizes how food delivery complaints are handled. Unlike traditional chatbots that immediately offer refunds, our agent follows a business-smart approach: **Evidence First, Solutions Second, Compensation Last**.

The system uses Google's Gemini AI with LangChain's ReAct framework to create an intelligent agent that can handle complex customer service scenarios while maintaining business sustainability and customer satisfaction.

## 🚀 Key Features

### 🧠 Intelligent Agent Core
- **Business-Conservative Approach**: Prioritizes evidence collection and solution-finding over immediate compensation
- **ReAct Framework**: Uses reasoning and action cycles for intelligent decision-making
- **Context-Aware**: Maintains conversation context and escalates appropriately
- **Multi-Tool Integration**: Seamlessly combines multiple specialized tools for comprehensive support

### 📸 Evidence Collection System
- **Visual Evidence Requests**: Automatically requests photos for spilled food, wrong orders, and packaging issues
- **Quality Assessment**: Analyzes customer descriptions to determine evidence requirements
- **Documentation**: Creates detailed evidence logs for business records
- **Smart Validation**: Distinguishes between visual issues requiring photos vs. service issues requiring different handling

### 💰 Conservative Compensation Management
- **Voucher-First Policy**: Offers vouchers (70-90% of order value) instead of immediate cash refunds
- **Goodwill Framing**: Presents compensation as "goodwill gestures" rather than fault admissions
- **Business Protection**: Prevents excessive compensation that could harm business sustainability
- **Escalation Triggers**: Only offers compensation for extremely dissatisfied customers

### 👥 Human Escalation System
- **Smart Officer Assignment**: Matches customers with specialized customer care officers based on issue type
- **Seamless Handoff**: Provides comprehensive case summaries to human agents
- **Officer Availability**: Real-time tracking of customer care officer status and specializations
- **Professional Transition**: Maintains conversation flow during escalation

### 📊 Feedback Intelligence
- **Issue Logging**: Records all customer feedback as valuable business intelligence
- **Merchant Analytics**: Tracks patterns in merchant-related issues
- **Driver Performance**: Monitors delivery-related complaints
- **Business Insights**: Generates actionable data for operational improvements

### 🎤 Speech-to-Text Integration
- **Voice Input**: Customers can speak their complaints instead of typing
- **Real-time Transcription**: Powered by AssemblyAI's advanced speech recognition
- **Language Detection**: Automatic language detection and transcription
- **Text Editing**: Users can review and edit transcribed text before submission
- **Accessibility**: Makes the system more accessible for users who prefer voice input

## 🔧 Technical Architecture

### Backend Infrastructure

#### Agent Core (`agent_core.py`)
```python
# Business-focused system message that emphasizes:
# 1. Evidence collection before any action
# 2. Professional feedback logging
# 3. Conservative compensation approach
# 4. Proper human escalation protocols
```

The agent uses a sophisticated prompt engineering approach that transforms it from a typical helpful AI into a business-savvy customer service representative.

#### Tool Management System (`tools.py`)
Our tool system is designed with business logic at its core:

**Evidence Collection Tools:**
- `request_visual_evidence()`: Intelligently requests photos based on issue type
- `log_customer_feedback()`: Professionally documents all customer concerns
- `analyze_customer_situation()`: Comprehensively evaluates complaints before action

**Compensation Management:**
- `offer_goodwill_voucher()`: Provides conservative voucher compensation (70-90%)
- `negotiate_fair_compensation()`: Business-focused negotiation framework
- `gather_compensation_details()`: Collects necessary information before any offers

**Human Escalation:**
- `escalate_to_customer_care_officer()`: Seamless handoff to human agents
- Officer matching based on specialization (Order Issues, Delivery Problems, Payment Issues)

### Sandbox Environment

#### Purpose & Design
The sandbox environment (`Sandbox/`) creates a realistic testing ecosystem that mimics Grab's actual operations:

**Realistic Data Simulation:**
```python
# Complete ecosystem with:
# - Customer profiles with order history
# - Merchant data with menu flexibility  
# - Driver information and performance metrics
# - Dynamic order creation based on user scenarios
# - Customer care officer availability tracking
```

**Key Components:**

1. **Dynamic Order Generation**: Creates realistic orders based on customer descriptions
2. **Business Logic Simulation**: Mimics real-world constraints and policies
3. **Multi-Entity Relationships**: Customers, merchants, drivers, and support staff interact naturally
4. **Evidence Processing**: Handles photo submissions and validation workflows
5. **Escalation Simulation**: Provides realistic customer care officer assignments

#### Sandbox Database (`sandbox_database.py`)
- **Customer Management**: Tracks order history, complaint patterns, wallet balances
- **Merchant Integration**: Maintains menu data, ratings, and issue tracking
- **Driver Coordination**: Performance metrics, delivery logs, incident reports
- **Officer Assignment**: Specialized customer care officers with expertise matching

### Web Interface

#### Flask Application (`app.py` & `flask_app.py`)
- **Professional UI**: Grab-branded interface with intuitive conversation flow
- **Real-time Chat**: Instant responses with typing indicators and professional styling
- **Evidence Upload**: Seamless photo submission and processing
- **Escalation Interface**: Smooth transition to human agents when needed

## 💡 Business Intelligence Features

### Smart Issue Classification
The system automatically categorizes complaints:
- **Visual Issues**: Spilled food, wrong orders, packaging problems → Photo evidence required
- **Service Issues**: Late delivery, driver behavior → Different handling approach
- **Payment Issues**: Billing problems, refund requests → Financial verification needed

### Merchant Feedback Loop
- Automatically logs issues with specific merchants
- Tracks patterns in food quality, packaging, and preparation
- Provides actionable data for merchant improvement programs

### Performance Analytics
- Customer satisfaction tracking
- Escalation rate monitoring  
- Evidence collection success rates
- Compensation cost management

## 🛡️ Business Protection Features

### Conservative Compensation Policy
- **Evidence Requirements**: No compensation without proper documentation
- **Voucher Priority**: Offers service credits instead of cash refunds
- **Escalation Thresholds**: Human intervention for high-value claims
- **Pattern Recognition**: Identifies potential abuse through complaint history

### Professional Communication
- **No Fault Admission**: Carefully worded responses that avoid liability
- **Feedback Framing**: Presents issues as "valuable improvement opportunities"
- **Goodwill Emphasis**: Positions compensation as customer retention investment
- **Documentation Standards**: Maintains detailed logs for business records


## 🚀 Getting Started

### Prerequisites
- **Python 3.8+**: Ensure you have Python installed
- **Google Gemini API Key**: Required for AI functionality
- **AssemblyAI API Key**: Required for speech-to-text functionality
- **Git**: For cloning the repository

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Ayush-D2004/Project_Synapse.git
   cd Project_Synapse
   ```

2. **Set Up Virtual Environment**
   ```bash
   # Windows
   python -m venv synapse
   synapse\Scripts\activate

   # macOS/Linux  
   python3 -m venv synapse
   source synapse/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   Create a `.env` file in the root directory:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
   ```

5. **Obtain API Keys**
   
   **Google Gemini API Key:**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy the key to your `.env` file
   
   **AssemblyAI API Key:**
   - Visit [AssemblyAI Console](https://www.assemblyai.com/app/account)
   - Sign up for a free account if you don't have one
   - Copy your API key from the dashboard
   - Add it to your `.env` file

### Running the Application

#### Flask Web Interface
```bash
python app.py
```
- Open your browser to `http://localhost:5000`
- Experience the full customer service interface
- Test evidence collection and escalation features


## 🆘 Support

For questions or issues:
1. Check the console logs for detailed error messages
2. Verify your Gemini API key is correctly configured
3. Verify your AssemblyAI API key is correctly configured
4. Ensure all dependencies are properly installed
5. Review the sandbox database for realistic test data
6. **For microphone issues**: Ensure browser permissions allow microphone access

**Note**: The speech-to-text feature requires microphone permissions in your browser. When prompted, please allow microphone access for voice input functionality.

**Built with ❤️ for smarter, more sustainable customer service automation**
