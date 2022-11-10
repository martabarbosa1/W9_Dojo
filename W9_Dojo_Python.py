# import libraries

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np
import seaborn as sns
import plotly.express as px

import mysql.connector 

from PIL import Image


#Connect to queries from SQL and create for each a dataframe

connection=mysql.connector.connect(user = 'toyscie', password = 'WILD4Rdata!', host = '51.68.18.102', port = '23456', database = 'toys_and_models')

#Query Sales
query_sales= '''WITH productline_quantity AS (
SELECT productline, YEAR(orderDate) order_year, SUM(quantityordered) order_quantity, MONTH(orderDate) order_month
FROM orders
INNER JOIN orderdetails USING (orderNumber)
INNER JOIN products USING (productCode)
GROUP BY productline, order_year, order_month
)
SELECT productline, order_year, order_month, order_quantity,
LAG(order_quantity, 1) OVER (
PARTITION BY productLine, order_month
ORDER BY order_month, order_year) as prev_year_order_quantity, (order_quantity * 100)/lag(order_quantity, 1) OVER (
        PARTITION BY productLine, order_month
        ORDER BY order_month, order_year) as ratechange
FROM
    productline_quantity'''

df_sales= pd.read_sql(query_sales, con=connection)

#Query Finances_turnover
query_finances_to='''select country, sum(priceeach*quantityordered) as turnover
from orders o
join orderdetails od on od.ordernumber=o.ordernumber
join customers c on c.customernumber=o.customernumber
WHERE orderdate >= DATE_FORMAT(CURDATE(), '%Y-%m-01') - INTERVAL 2 MONTH
Group by country
order by turnover desc''' 

df_finances_to = pd.read_sql(query_finances_to, con=connection)
df_finances_to.head(7)

#Query Finances_orders
query_finances_o= '''select o.customernumber, sum(distinct od.quantityordered*od.priceEach) as Total_Amount_Ordered, sum(distinct p.amount) as Total_Amount_Paid, sum(distinct od.quantityordered*od.priceEach) - sum(distinct p.amount) as difference
from orderdetails od
join orders o on o.ordernumber=od.ordernumber
join payments p on p.customernumber=o.customernumber
group by customernumber
having difference > 0'''


df_finances_o = pd.read_sql(query_finances_o, con=connection)
df_finances_o.head(12)

#Query Logistics
query_logistics= '''select p.productname,p.productline, sum(od.quantityordered) as sumOrdered, p.quantityinstock from products p join orderdetails od on p.productcode=od.productCode
group by p.productname
order by sumOrdered desc
limit 5'''

df_logistics=pd.read_sql(query_logistics, con=connection)

#Query HR
query_hr= '''WITH top_sellers AS (select e.employeeNumber, e.firstname, jobTitle, e.lastname, DATE_FORMAT(o.orderdate, "%c %Y") as DateOrd, year(o.orderdate) as YearOrd, month(o.orderdate) as month_,sum(od.quantityordered*od.priceeach) as highest_turnover,
RANK() OVER (PARTITION BY DateOrd ORDER BY highest_turnover DESC) sell_rank from employees e
join customers c on e.employeeNumber=c.salesRepEmployeeNumber
join orders o on c.customerNumber=o.customerNumber
join orderdetails od on o.orderNumber=od.orderNumber
WHERE jobTitle like 'Sales Rep%' and o.status <> 'Cancelled'
Group by DateOrd, employeeNumber
Order by DateOrd, highest_turnover DESC)
select * from top_sellers
where sell_rank=1 or sell_rank=2;'''

df_hr = pd.read_sql(query_hr, con=connection)
df_hr.head(53)
df_hr = df_hr[df_hr['YearOrd'] == 2021]
print(df_hr)


#Streamilt code

#Page configuration to wide
st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

#Organize space in columns_1st line
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    image1 = Image.open('./Image1.JPG')
    image1t = image1.transpose(Image.FLIP_LEFT_RIGHT)
    # image1ts = image1t.resize((300, 200))
    st.image(image1t, width=300)
    
with col2:
    st.title('')
    
with col3:
    st.markdown("<h1 style='text-align: center; color: Grey;'>Models and Toys</h1>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: Blue;'>Sales at a glance</h1>", unsafe_allow_html=True)
    
with col4:
    st.title('')
    
with col5:
    image1s = Image.open('./Image1.JPG')
    # image1s = image1s.resize((300, 200))
    st.image(image1s, width=300)
    
    
#Organize space in columns_2nd line  
col1, col2, col3 = st.columns(3)

with col1:  
    st.subheader('''The turnover of the orders of the last two months by country:''')
    # st.info('Information from last 2 months', icon="ℹ️")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(df_finances_to["country"], df_finances_to["turnover"], color="grey")
    ax.set_title('The turnover of orders')
    ax.set_ylabel('Orders')
    ax.set_xlabel('Country')
    fig.autofmt_xdate()
    st.pyplot(fig)
    st.set_option('deprecation.showPyplotGlobalUse', False)

    
with col2:
    st.subheader('''The rate of change compared to the same month of the previous year:''')
    fig2, ax2 = plt.subplots(figsize=(10,4))
    colors=['grey', 'black', 'blue']
    sns.barplot(data=df_sales, x="order_month", y="ratechange", hue="order_year", ci=None, palette=colors)
    ax2.set_xlabel("Month")
    ax2.set_ylabel("Rate of change (%)")
    ax2.legend(title="Year: ")
    ax2.set_title('Rate of change')
    st.pyplot(fig2)

   
with col3:
    st.subheader('''The number of products sold by category:''')
    fig3, ax3 = plt.subplots(figsize=(10,4))
    colors=['grey', 'black', 'blue']
    sns.barplot(data=df_sales, x="productline", y="order_quantity", hue="order_year", ci=None, palette=colors)
    ax3.set_xlabel("Categories")
    ax3.set_ylabel("# orders")
    ax3.legend(title="Year: ")
    ax3.set_title('# products by category')
    st.pyplot(fig3)

    
#Organize space in columns_3rd line
col1, col2, col3 = st.columns(3)

with col1:  
    st.text_area('', '''
    The countries with less sales are Austria, Spain and USA.''') 
    
with col2:
    st.text_area('', '''The orders are increasing in all months compared with the previous year. 
    Nevertheless, we can try to increase sales:
    in the months with less than 25% of the best months...''') 
   
with col3:
    st.text_area('', '''The orders are increasing across all the categories (except for planes and trains).
    We should try to increase sales at least in planes + trains...''') 
    

#End