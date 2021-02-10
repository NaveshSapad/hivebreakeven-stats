#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from hiveengine.market import Market
from hiveengine.api import Api
import time
from datetime import datetime as dt
import streamlit as st

def get_history(user,token): 
    end=0
    x=0
    s=[]
    
    progress_details.write("Gathering your {} details ".format(token))
    
    
    while(end!=1):
        time.sleep(0.02)
        res=api.get_history(user,token,offset=x)
        s.append(res)

        x=x+len(res)
        if(len(res)<500):
            end=1

    listfinal=[]
    for i in range(0,len(s)):
        for j in range(0,len(s[i])):
            listfinal.append(s[i][j])
            
    progress_bar.progress(20)
    
    return(listfinal)

def get_buy_sell_history(listfinal,token):
    buy_list=[]
    sell_list=[]
    progress_details.write(" Retreiving your {} market transactions ".format(token))
    for i in range(0,len(listfinal)):
        if(listfinal[i]['operation']=='market_buy' or listfinal[i]['operation']=='market_sell'):
            if(listfinal[i]['operation']=='market_buy'):
                buy_list.append([listfinal[i]['quantityTokens'],str((float(listfinal[i]['quantitySteem'])/float(listfinal[i]['quantityTokens']))),time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(listfinal[i]['timestamp']))])
            elif(listfinal[i]['operation']=='market_sell'):
                sell_list.append([listfinal[i]['quantityTokens'],str((float(listfinal[i]['quantitySteem'])/float(listfinal[i]['quantityTokens']))),time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(listfinal[i]['timestamp']))])
    
    progress_bar.progress(40)
    return(buy_list,sell_list)

def get_transfer_history(user,token):
    add_q=0
    sub_q=0
    add_list=[]
    sub_list=[]
    progress_details.write("Retreiving details regarding {} received and sent to your account".format(token))
    for i in range(0,len(listfinal)):
        if(listfinal[i]['operation']=='tokens_stake'):
            if(listfinal[i]['from']!=user):
                add_q += float(listfinal[i]['quantity'])
                add_list.append([listfinal[i]['from'],listfinal[i]['quantity'],time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(listfinal[i]['timestamp']))])
            else:
                if(listfinal[i]['to']!=user):
                    sub_q += float(listfinal[i]['quantity'])
                    sub_list.append([listfinal[i]['to'],listfinal[i]['quantity'],time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(listfinal[i]['timestamp']))])
            
        if(listfinal[i]['operation']=='tokens_transfer' or listfinal[i]['operation']=='tokens_issue'):
            if(listfinal[i]['from']!=user):
                add_q += float(listfinal[i]['quantity'])
                add_list.append([listfinal[i]['from'],listfinal[i]['quantity'],time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(listfinal[i]['timestamp']))])
            else:
                sub_q += float(listfinal[i]['quantity'])
                sub_list.append([listfinal[i]['to'],listfinal[i]['quantity'],time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(listfinal[i]['timestamp']))])
                
    progress_bar.progress(60)
                
    return(add_q,sub_q,add_list,sub_list)

def calculate_current_avg(buy_list,sell_list,user,token):
    
    if not buy_list:
        df_buy = pd.DataFrame(columns = ['Quantity','Price','Date'])
    else:
        df_buy=pd.DataFrame(buy_list)
        
    if not sell_list:
        df_sell = pd.DataFrame(columns = ['Quantity','Price','Date'])
    else:
        df_sell=pd.DataFrame(sell_list)

    df_buy.columns=['Quantity','Price','Date']
    df_sell.columns=['Quantity','Price','Date']

    df_buy['Quantity']=pd.to_numeric(df_buy['Quantity'])
    df_buy['Price']=pd.to_numeric(df_buy['Price'])
    

    df_sell['Quantity']=pd.to_numeric(df_sell['Quantity'])
    df_sell['Price']=pd.to_numeric(df_sell['Price'])

    df_buy['Hive_paid_total']=df_buy['Quantity']*df_buy['Price']
    df_sell['Hive_got_total']=df_sell['Quantity']*df_sell['Price']

    buy_total=df_buy['Hive_paid_total'].sum()
    buy_q=df_buy['Quantity'].sum()
    avg_buy=buy_total/buy_q
    
    if first.checkbox("Click to see your buy_history"):
        buy_history.table(df_buy)
    
    if second.checkbox("Click to see your sell_history"):
        sell_history.table(df_sell)

    print('\nAverage price (BUY):'+str(avg_buy)+' Amount:'+str(buy_q))


    sell_total=df_sell['Hive_got_total'].sum()
    sell_q=df_sell['Quantity'].sum()
    avg_sell=sell_total/sell_q


    buy_avg.write("You have bought <b>{}</b> {} totally - Average buy price : {}".format(buy_q,token,avg_buy),unsafe_allow_html=True)
    sell_avg.write("You have sold <b>{}</b> {} totally - Average sell price : {}".format(sell_q,token,avg_sell),unsafe_allow_html=True)
    
    print('\nAverage price (SELL):'+str(avg_sell)+' Amount:'+str(sell_q))
    
    
    add_q,sub_q,add_list,sub_list=get_transfer_history(user,token)
    progress_details.write("Final calculation...")

    what_you_got.write("You have received <b>{}</b> {} from others ".format(add_q,token),unsafe_allow_html=True)
    what_you_sent.write("You have sent <b>{}</b> {} to others ".format(sub_q,token),unsafe_allow_html=True)
    
    print("\nSent:"+str(sub_q),"Received:"+str(add_q))
    
    profit=buy_total-sell_total
    remaining_amount=buy_q+add_q-sell_q-sub_q
    current_avg= (profit)/(remaining_amount)
    
    progress_bar.progress(80)

    if not add_list:
        df_receive= pd.DataFrame(columns=['From','Quantity','Date'])
    else:
        df_receive= pd.DataFrame(add_list)
        df_receive.columns=['From','Quantity','Date']

    if not sub_list:
        df_send= pd.DataFrame(columns=['To','Quantity','Date'])

    else:   
        df_send=pd.DataFrame(sub_list)
        df_send.columns=['To','Quantity','Date']
    
    if third.checkbox("Click to see your received_history"):
        receive.table(df_receive)
    
    if fourth.checkbox("Click to see your send_history"):
        send.table(df_send)
    
    
    return(remaining_amount,current_avg,profit)

def get_sym_list():
    market= Market()
    market_details=market.get_metrics()
    symbols_list=[]
    for i in range(0,len(market_details)):
        symbols_list.append(market_details[i]['symbol'])
        
    return symbols_list
    
    
if __name__ == '__main__':
    
    
    api=Api()

    st.set_page_config(page_title='Hive 2nd layer Earnings stats',layout='wide')
    
    st.markdown("<h1><center> Enter your username and the token you wish to see the details for and click enter </center></h1>",unsafe_allow_html=True)
    
    symbols_list= get_sym_list()
    
    entry,output = st.beta_columns(2)
    
    user=entry.text_input("Enter the username:")
    token=entry.selectbox("Enter the token:",symbols_list)
    user=user.lower()
    token=token.upper()
    
    if user:
        if token:
            progress_details= entry.empty()
            progress_bar= entry.progress(0)
            
            output.markdown("<h4><center> You can view your details here </center></h4>",unsafe_allow_html=True)
            

            buy_avg=output.empty()
            sell_avg=output.empty()
            what_you_got=output.empty()
            what_you_sent=output.empty()

            output.write("<hr>",unsafe_allow_html=True)

            first=output.empty()
            buy_history = output.empty()
            second=output.empty()
            sell_history = output.empty()
            third=output.empty()
            receive = output.empty()
            fourth=output.empty()
            send = output.empty()



            listfinal=get_history(user,token)

            buy_list,sell_list=get_buy_sell_history(listfinal,token)

            current_holdings,current_avg,profit=calculate_current_avg(buy_list,sell_list,user,token)

            progress_details.write("Successfully fetched all the details")

            entry.markdown("<h4><center>Current Holdings is : {} {}</center></h4><br><hr>".format(current_holdings,token),unsafe_allow_html=True)


            if(current_avg>0):
                current_avg= abs(current_avg)
                entry.markdown("<h3><center>Current_avg( HIVE ):{} per {}<h6><center>Formula used: (Buy_total - sell_total) / (Buy_quantity+ received_amount - sell_quantity - sent_amount)</center></h6><br><hr> That means you can sell the {} at any price greater than {} HIVE to make profits .<br><hr>If you sell for less , you will make loss.</center></h3>".format('%.8f' % current_avg,token,token,'%.8f' % current_avg),unsafe_allow_html=True) 

            elif(current_avg!=0 and profit!=0):
                entry.markdown("<h3><center>Cool , you are on profits already .Total profits so far: {} HIVE.<br><hr> Don't forget you still hold {} amount of {} token</center></h3>".format(str(abs(profit)),"%.6f" % current_holdings,token),unsafe_allow_html=True)
            else:
                entry.markdown("<h3><center>No profit , no loss</center></h3>",unsafe_allow_html=True)
                
            progress_bar.progress(100)
        else:
            st.write("Please enter token")
            
    else:
        st.write("Please enter both Username and token")

