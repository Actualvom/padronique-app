#!/usr/bin/env python3
"""
finance_brain.py: Provides financial assistance and tracking.
"""

import time
import re
import random
from datetime import datetime
from brains.base_brain import BaseBrain

class FinanceBrain(BaseBrain):
    """
    Finance Brain responsible for financial assistance and tracking.
    Helps with budgeting, expense tracking, and financial education.
    """
    
    def __init__(self):
        """Initialize the Finance Brain."""
        super().__init__("Finance")
        self.digital_soul = None  # Will be set by orchestrator
        self.finances = {
            "expenses": [],
            "income": [],
            "budget": {},
            "goals": []
        }
        self.categories = [
            "housing", "utilities", "food", "transportation", "healthcare",
            "entertainment", "shopping", "education", "savings", "debt", "other"
        ]
    
    def process_input(self, input_data):
        """
        Process input data for finance-related queries.
        
        Args:
            input_data: Input data to process
            
        Returns:
            str: Response with financial information or None
        """
        super().process_input(input_data)
        
        # Skip cycle updates
        if input_data == "Cycle update":
            return None
        
        # Skip if not finance-related
        if not self._is_finance_related(input_data):
            return None
        
        try:
            # Identify the finance function
            finance_function = self._identify_finance_function(input_data)
            
            # Handle different finance functions
            if finance_function == "track_expense":
                return self._handle_expense_tracking(input_data)
            elif finance_function == "track_income":
                return self._handle_income_tracking(input_data)
            elif finance_function == "budget":
                return self._handle_budget_request(input_data)
            elif finance_function == "goal":
                return self._handle_goal_request(input_data)
            elif finance_function == "report":
                return self._generate_finance_report(input_data)
            elif finance_function == "advice":
                return self._provide_financial_advice(input_data)
            else:
                return self._generate_general_finance_info()
            
        except Exception as e:
            self.logger.error(f"Error processing finance input: {e}")
            self.stats["error_count"] += 1
            return None
    
    def _is_finance_related(self, text):
        """
        Determine if input is related to finance.
        
        Args:
            text: Input text
            
        Returns:
            bool: True if finance-related
        """
        text_lower = text.lower()
        
        # Check for finance-related keywords
        finance_keywords = [
            "money", "finance", "financial", "budget", "expense", "income",
            "spend", "spent", "cost", "bill", "payment", "pay", "debt",
            "loan", "credit", "savings", "save", "invest", "investment",
            "bank", "account", "transaction", "purchase", "bought", "salary",
            "wage", "tax", "taxes", "mortgage", "rent", "dollar", "dollars", "$"
        ]
        
        return any(keyword in text_lower for keyword in finance_keywords)
    
    def _identify_finance_function(self, text):
        """
        Identify the finance function being requested.
        
        Args:
            text: Input text
            
        Returns:
            str: Finance function
        """
        text_lower = text.lower()
        
        # Check for expense tracking
        if any(phrase in text_lower for phrase in ["spent", "bought", "purchased", "paid", "expense", "cost me"]):
            if "$" in text or "dollar" in text_lower or re.search(r"\d+(\.\d+)?", text):
                return "track_expense"
        
        # Check for income tracking
        if any(phrase in text_lower for phrase in ["earned", "received", "got paid", "income", "salary", "wage"]):
            if "$" in text or "dollar" in text_lower or re.search(r"\d+(\.\d+)?", text):
                return "track_income"
        
        # Check for budget requests
        if any(phrase in text_lower for phrase in ["budget", "spending limit", "allocate", "set aside"]):
            return "budget"
        
        # Check for goal requests
        if any(phrase in text_lower for phrase in ["goal", "saving for", "want to save", "financial target"]):
            return "goal"
        
        # Check for report requests
        if any(phrase in text_lower for phrase in ["summary", "report", "overview", "show me", "how much", "status"]):
            return "report"
        
        # Check for advice requests
        if any(phrase in text_lower for phrase in ["advice", "suggest", "help me with", "what should", "recommend"]):
            return "advice"
        
        # Default to general
        return "general"
    
    def _handle_expense_tracking(self, text):
        """
        Handle expense tracking requests.
        
        Args:
            text: Input text
            
        Returns:
            str: Response
        """
        # Extract amount
        amount_match = re.search(r"\$?(\d+(?:\.\d+)?)", text)
        if not amount_match:
            return "I couldn't identify the expense amount. Please specify how much you spent, for example: 'I spent $45.30 on groceries'."
        
        amount = float(amount_match.group(1))
        
        # Extract category
        category = "other"
        text_lower = text.lower()
        for cat in self.categories:
            if cat in text_lower:
                category = cat
                break
        
        # Extract date (default to today)
        date_str = datetime.now().strftime("%Y-%m-%d")
        timestamp = time.time()
        
        # Create expense entry
        expense = {
            "amount": amount,
            "category": category,
            "date": date_str,
            "timestamp": timestamp,
            "description": text  # Store original text as description
        }
        
        # Add to expenses
        self.finances["expenses"].append(expense)
        
        # Generate response
        category_display = category.capitalize()
        return f"I've recorded your {category_display} expense of ${amount:.2f} on {date_str}."
    
    def _handle_income_tracking(self, text):
        """
        Handle income tracking requests.
        
        Args:
            text: Input text
            
        Returns:
            str: Response
        """
        # Extract amount
        amount_match = re.search(r"\$?(\d+(?:\.\d+)?)", text)
        if not amount_match:
            return "I couldn't identify the income amount. Please specify how much you received, for example: 'I earned $1200 from my job'."
        
        amount = float(amount_match.group(1))
        
        # Extract source
        source = "other"
        text_lower = text.lower()
        
        # Common income sources
        sources = ["salary", "wage", "freelance", "gift", "bonus", "interest", "dividend", "refund", "side hustle"]
        for src in sources:
            if src in text_lower:
                source = src
                break
        
        # Extract date (default to today)
        date_str = datetime.now().strftime("%Y-%m-%d")
        timestamp = time.time()
        
        # Create income entry
        income = {
            "amount": amount,
            "source": source,
            "date": date_str,
            "timestamp": timestamp,
            "description": text  # Store original text as description
        }
        
        # Add to income
        self.finances["income"].append(income)
        
        # Generate response
        source_display = source.capitalize()
        return f"I've recorded your {source_display} income of ${amount:.2f} on {date_str}."
    
    def _handle_budget_request(self, text):
        """
        Handle budget creation or modification requests.
        
        Args:
            text: Input text
            
        Returns:
            str: Response
        """
        text_lower = text.lower()
        
        # Check if this is a request to view the budget
        if "view" in text_lower or "show" in text_lower or "what is" in text_lower:
            return self._show_budget()
        
        # Check if this is setting a budget for a specific category
        for category in self.categories:
            if category in text_lower:
                # Extract amount
                amount_match = re.search(r"\$?(\d+(?:\.\d+)?)", text)
                if amount_match:
                    amount = float(amount_match.group(1))
                    self.finances["budget"][category] = amount
                    return f"I've set your {category.capitalize()} budget to ${amount:.2f} per month."
        
        # If we couldn't parse a specific budget request
        return "I can help you set or view your budget. To set a budget for a category, say something like 'Set my food budget to $500'."
    
    def _handle_goal_request(self, text):
        """
        Handle financial goal requests.
        
        Args:
            text: Input text
            
        Returns:
            str: Response
        """
        text_lower = text.lower()
        
        # Check if this is a request to view goals
        if "view" in text_lower or "show" in text_lower or "list" in text_lower:
            return self._show_goals()
        
        # Check if this is setting a new goal
        if "new" in text_lower or "add" in text_lower or "create" in text_lower or "set" in text_lower:
            # Extract amount
            amount_match = re.search(r"\$?(\d+(?:\.\d+)?)", text)
            if not amount_match:
                return "I couldn't identify the goal amount. Please specify an amount, for example: 'I want to save $5000 for a vacation'."
            
            amount = float(amount_match.group(1))
            
            # Extract description (anything after "for" or "to")
            description = "savings goal"
            for_match = re.search(r"for (.*?)($|\.|,)", text)
            to_match = re.search(r"to (.*?)($|\.|,)", text)
            
            if for_match:
                description = for_match.group(1).strip()
            elif to_match:
                description = to_match.group(1).strip()
            
            # Create goal entry
            goal = {
                "amount": amount,
                "description": description,
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "target_date": None,  # Could parse this from text in a more advanced implementation
                "current_amount": 0.0
            }
            
            # Add to goals
            self.finances["goals"].append(goal)
            
            return f"I've added your goal to save ${amount:.2f} for {description}."
        
        # If we couldn't parse a specific goal request
        return "I can help you set or view your financial goals. To set a new goal, say something like 'I want to save $5000 for a vacation'."
    
    def _generate_finance_report(self, text):
        """
        Generate a financial report.
        
        Args:
            text: Input text
            
        Returns:
            str: Finance report
        """
        text_lower = text.lower()
        
        # Check what type of report is requested
        if "expense" in text_lower or "spending" in text_lower:
            return self._generate_expense_report()
        elif "income" in text_lower or "earning" in text_lower:
            return self._generate_income_report()
        elif "overview" in text_lower or "summary" in text_lower:
            return self._generate_financial_summary()
        else:
            # Default to comprehensive summary
            return self._generate_financial_summary()
    
    def _generate_expense_report(self):
        """
        Generate an expense report.
        
        Returns:
            str: Expense report
        """
        if not self.finances["expenses"]:
            return "You haven't recorded any expenses yet. You can track expenses by telling me what you've spent."
        
        # Sort expenses by date (most recent first)
        sorted_expenses = sorted(self.finances["expenses"], key=lambda x: x["timestamp"], reverse=True)
        
        # Take the 10 most recent expenses
        recent_expenses = sorted_expenses[:10]
        
        # Calculate total expenses
        total_expenses = sum(expense["amount"] for expense in self.finances["expenses"])
        
        # Calculate category totals
        category_totals = {}
        for expense in self.finances["expenses"]:
            category = expense["category"]
            amount = expense["amount"]
            if category in category_totals:
                category_totals[category] += amount
            else:
                category_totals[category] = amount
        
        # Sort categories by amount (highest first)
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        
        # Generate report
        report = "Expense Report:\n\n"
        
        # Total expenses
        report += f"Total Expenses: ${total_expenses:.2f}\n\n"
        
        # Category breakdown
        report += "Top Categories:\n"
        for category, amount in sorted_categories[:5]:  # Show top 5 categories
            percentage = (amount / total_expenses) * 100 if total_expenses > 0 else 0
            report += f"- {category.capitalize()}: ${amount:.2f} ({percentage:.1f}%)\n"
        
        # Recent expenses
        report += "\nRecent Expenses:\n"
        for expense in recent_expenses:
            date = expense["date"]
            amount = expense["amount"]
            category = expense["category"].capitalize()
            report += f"- {date}: ${amount:.2f} ({category})\n"
        
        return report
    
    def _generate_income_report(self):
        """
        Generate an income report.
        
        Returns:
            str: Income report
        """
        if not self.finances["income"]:
            return "You haven't recorded any income yet. You can track income by telling me what you've earned."
        
        # Sort income by date (most recent first)
        sorted_income = sorted(self.finances["income"], key=lambda x: x["timestamp"], reverse=True)
        
        # Take the 10 most recent income entries
        recent_income = sorted_income[:10]
        
        # Calculate total income
        total_income = sum(entry["amount"] for entry in self.finances["income"])
        
        # Calculate source totals
        source_totals = {}
        for entry in self.finances["income"]:
            source = entry["source"]
            amount = entry["amount"]
            if source in source_totals:
                source_totals[source] += amount
            else:
                source_totals[source] = amount
        
        # Sort sources by amount (highest first)
        sorted_sources = sorted(source_totals.items(), key=lambda x: x[1], reverse=True)
        
        # Generate report
        report = "Income Report:\n\n"
        
        # Total income
        report += f"Total Income: ${total_income:.2f}\n\n"
        
        # Source breakdown
        report += "Income Sources:\n"
        for source, amount in sorted_sources:
            percentage = (amount / total_income) * 100 if total_income > 0 else 0
            report += f"- {source.capitalize()}: ${amount:.2f} ({percentage:.1f}%)\n"
        
        # Recent income
        report += "\nRecent Income:\n"
        for entry in recent_income:
            date = entry["date"]
            amount = entry["amount"]
            source = entry["source"].capitalize()
            report += f"- {date}: ${amount:.2f} ({source})\n"
        
        return report
    
    def _generate_financial_summary(self):
        """
        Generate a comprehensive financial summary.
        
        Returns:
            str: Financial summary
        """
        # Calculate totals
        total_income = sum(entry["amount"] for entry in self.finances["income"])
        total_expenses = sum(expense["amount"] for expense in self.finances["expenses"])
        net = total_income - total_expenses
        
        # Generate summary
        summary = "Financial Summary:\n\n"
        
        # Income and expenses
        summary += f"Total Income: ${total_income:.2f}\n"
        summary += f"Total Expenses: ${total_expenses:.2f}\n"
        summary += f"Net (Income - Expenses): ${net:.2f}\n\n"
        
        # Budget status
        if self.finances["budget"]:
            summary += "Budget Status:\n"
            
            # Calculate category totals for current month
            current_month = datetime.now().strftime("%Y-%m")
            category_totals = {}
            
            for expense in self.finances["expenses"]:
                if expense["date"].startswith(current_month):
                    category = expense["category"]
                    amount = expense["amount"]
                    if category in category_totals:
                        category_totals[category] += amount
                    else:
                        category_totals[category] = amount
            
            # Compare with budget
            for category, budget in self.finances["budget"].items():
                spent = category_totals.get(category, 0)
                remaining = budget - spent
                percentage = (spent / budget) * 100 if budget > 0 else 0
                
                summary += f"- {category.capitalize()}: ${spent:.2f} of ${budget:.2f} ({percentage:.1f}%)"
                if remaining < 0:
                    summary += f" [Over budget by ${abs(remaining):.2f}]"
                else:
                    summary += f" [${remaining:.2f} remaining]"
                summary += "\n"
        
        # Goals status
        if self.finances["goals"]:
            summary += "\nFinancial Goals:\n"
            for goal in self.finances["goals"]:
                amount = goal["amount"]
                current = goal["current_amount"]
                description = goal["description"]
                percentage = (current / amount) * 100 if amount > 0 else 0
                
                summary += f"- {description}: ${current:.2f} of ${amount:.2f} ({percentage:.1f}% complete)\n"
        
        return summary
    
    def _provide_financial_advice(self, text):
        """
        Provide financial advice based on the input.
        
        Args:
            text: Input text
            
        Returns:
            str: Financial advice
        """
        text_lower = text.lower()
        
        # Check for specific advice topics
        if "budget" in text_lower:
            return self._get_budgeting_advice()
        elif "save" in text_lower or "saving" in text_lower:
            return self._get_saving_advice()
        elif "invest" in text_lower or "investment" in text_lower:
            return self._get_investment_advice()
        elif "debt" in text_lower or "loan" in text_lower or "credit" in text_lower:
            return self._get_debt_advice()
        else:
            return self._get_general_financial_advice()
    
    def _get_budgeting_advice(self):
        """
        Get budgeting advice.
        
        Returns:
            str: Budgeting advice
        """
        advice = [
            "Consider using the 50/30/20 rule: 50% of income for needs, 30% for wants, and 20% for savings and debt repayment.",
            "Track all expenses for a month before creating a budget to get an accurate picture of your spending habits.",
            "Review and adjust your budget regularly as your financial situation and goals change.",
            "Use automatic transfers to ensure you're contributing to savings before you have a chance to spend the money.",
            "Consider using cash for discretionary spending to make it more tangible and help you stick to your budget."
        ]
        
        return "Budgeting Advice: " + random.choice(advice)
    
    def _get_saving_advice(self):
        """
        Get saving advice.
        
        Returns:
            str: Saving advice
        """
        advice = [
            "Build an emergency fund with 3-6 months of essential expenses before focusing on other savings goals.",
            "Automate your savings by setting up automatic transfers to a separate savings account.",
            "Consider high-yield savings accounts or certificates of deposit for funds you don't need immediate access to.",
            "Set specific, measurable savings goals with deadlines to stay motivated.",
            "Look for small, regular expenses you can reduce or eliminate, and redirect that money to savings."
        ]
        
        return "Saving Advice: " + random.choice(advice)
    
    def _get_investment_advice(self):
        """
        Get investment advice.
        
        Returns:
            str: Investment advice
        """
        advice = [
            "Consider starting with low-cost index funds if you're new to investing.",
            "Diversification across different asset classes can help manage risk in your investment portfolio.",
            "Time in the market is generally more important than timing the market for long-term investments.",
            "Consider tax-advantaged accounts like 401(k)s or IRAs for retirement savings.",
            "Regularly rebalance your investment portfolio to maintain your desired asset allocation."
        ]
        
        return "Investment Advice: " + random.choice(advice) + "\n\nNote: This is general information, not personalized investment advice. Consider consulting with a financial advisor for advice tailored to your situation."
    
    def _get_debt_advice(self):
        """
        Get debt management advice.
        
        Returns:
            str: Debt advice
        """
        advice = [
            "Consider the debt avalanche method (paying off highest interest debt first) to minimize interest costs.",
            "The debt snowball method (paying off smallest debts first) can provide psychological wins to keep you motivated.",
            "Look into balance transfers or debt consolidation for high-interest debts if you qualify for lower rates.",
            "Always pay at least the minimum on all debts to avoid late fees and credit score damage.",
            "Consider talking to creditors about hardship programs or negotiating lower interest rates if you're struggling."
        ]
        
        return "Debt Management Advice: " + random.choice(advice)
    
    def _get_general_financial_advice(self):
        """
        Get general financial advice.
        
        Returns:
            str: General financial advice
        """
        advice = [
            "Review your financial goals regularly and adjust your plan as needed to stay on track.",
            "Consider building an emergency fund with 3-6 months of essential expenses before focusing on other financial goals.",
            "Regularly review your credit report for errors and to monitor your financial health.",
            "When making large purchases, consider the total cost of ownership, not just the purchase price.",
            "Financial education is an ongoing process—consider reading books, taking courses, or following reputable financial blogs to continue learning."
        ]
        
        return "Financial Advice: " + random.choice(advice) + "\n\nNote: This is general information, not personalized financial advice. Consider consulting with a financial advisor for advice tailored to your situation."
    
    def _show_budget(self):
        """
        Show the current budget.
        
        Returns:
            str: Budget information
        """
        if not self.finances["budget"]:
            return "You haven't set up a budget yet. You can create a budget by telling me something like 'Set my food budget to $500'."
        
        response = "Your Monthly Budget:\n\n"
        
        total_budget = sum(self.finances["budget"].values())
        
        # Show budgeted categories
        for category, amount in self.finances["budget"].items():
            percentage = (amount / total_budget) * 100 if total_budget > 0 else 0
            response += f"{category.capitalize()}: ${amount:.2f} ({percentage:.1f}%)\n"
        
        response += f"\nTotal Budgeted: ${total_budget:.2f}"
        
        return response
    
    def _show_goals(self):
        """
        Show current financial goals.
        
        Returns:
            str: Goals information
        """
        if not self.finances["goals"]:
            return "You haven't set any financial goals yet. You can create a goal by telling me something like 'I want to save $5000 for a vacation'."
        
        response = "Your Financial Goals:\n\n"
        
        for i, goal in enumerate(self.finances["goals"], 1):
            amount = goal["amount"]
            current = goal["current_amount"]
            description = goal["description"]
            percentage = (current / amount) * 100 if amount > 0 else 0
            
            response += f"{i}. {description}:\n"
            response += f"   Target: ${amount:.2f}\n"
            response += f"   Progress: ${current:.2f} ({percentage:.1f}%)\n"
            
            if goal["target_date"]:
                response += f"   Target Date: {goal['target_date']}\n"
            
            response += "\n"
        
        return response
    
    def _generate_general_finance_info(self):
        """
        Generate general financial information.
        
        Returns:
            str: General finance information
        """
        general_info = [
            "I can help you track expenses, record income, set budgets, and monitor financial goals. What would you like to do?",
            "Regular financial reviews can help you stay on track with your goals. Would you like to see a summary of your finances?",
            "Setting specific, measurable financial goals is a key step toward financial well-being. Would you like to set a financial goal?",
            "Tracking your expenses is the first step to understanding and improving your financial situation. You can tell me about expenses by saying something like 'I spent $45 on groceries'.",
            "Building a budget that aligns with your values and goals can help you make more intentional financial decisions. Would you like help creating a budget?"
        ]
        
        return random.choice(general_info)
