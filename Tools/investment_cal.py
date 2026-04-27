from langchain.tools import tool
@tool
def investment_cal(monthly_investment:float,annual_return:float,years:int) -> str:
    """"
    Calculate future value of monthly investment using compound interest.
    """
    monthly_rate=annual_return /100 /12
    months=years*12

    future_value=monthly_investment*(((1+monthly_rate)**months -1)/monthly_rate)
    return f"If you invest Rs{monthly_investment} monthly for {years} years at {annual_return}% annual return,your investment could grow to approximately ₹{round(future_value,2)}."
