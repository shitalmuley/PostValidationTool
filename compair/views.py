# import XlsxWriter
from asyncio.windows_events import NULL
# from multiprocessing import connection
from sqlite3 import dbapi2
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
import pandas as pd
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import mimetypes
import datacompy
import cx_Oracle
import win32api
import os
import sys
import time
import pyodbc
import pymssql
import ibm_db
cx_Oracle.init_oracle_client(lib_dir=r"C:\instantclient_19_9")


Data = ''

# Code for Excel Comparison
def excel(request):
    context = {}
    if request.method == 'POST':

        SRC_file = request.FILES['SRC_FILE']  # catch and perform code on it
        TGT_file = request.FILES['TGT_FILE']  # catch and perform code on it
        fs = FileSystemStorage()

        SRC_FILE = fs.save(SRC_file.name, SRC_file)
        TGT_FILE = fs.save(TGT_file.name, TGT_file)

        print("file reading started ")
        df1 = pd.read_excel(SRC_file)
        df2 = pd.read_excel(TGT_file)

        print("comparison START")
        compare = datacompy.Compare(
            df1, df2, join_columns=f'{df1.columns[0]}', df1_name='SRC_DATA',
            df2_name='TGT_DATA')
        text_report = compare.report()
        file_report_txt = settings.DATA_DIR/'TableReprort.txt'
        report_file = open(file_report_txt, 'w', encoding="utf-8")
        report_file.write(text_report)
        report_file.close()
        print("comparison END")
        # EXCEL DIFFERENCE

        df1.rename(columns=lambda x: x + '_S')
        df2.rename(columns=lambda x: x + '_T', inplace=True)
        print("DF RENAMEING OK",len(df1.columns))

        list1 = []
        list2 = []
        for x in df1.columns:
            # print("hi",x)
            new_x=x.replace(x,x+"_T")
            # print("new x : ",new_x)
            for y in df2.columns:
                # print("bye",y)
                
                if new_x==y:
                    # print("col1 : ",x)
                    
                    # print(df_join)
                    # print("x :",df1)
                    # print("value",x)
                    list1.append(x)
                    list2.append(y)
                    df_join = df1.merge(right=df2,
                                            left_on=list1,
                                            right_on=list2,
                                            how='left')
                    # print("list 1 :  ",list1)
                    # sorting the excel record on matching (JOIN)
        print("list 1 : ",list1[0])
        print("list 2 : ",list2[0])
        # records_present_in_df1_not_in_df2 = df_join.loc[df_join[list2], list1]
        # records_present_in_df2_not_in_df1 = df_join.loc[df_join[list1], list2]
        records_present_in_df1_not_in_df2 = df_join.loc[df_join[list2].isnull().all(axis=1), list1]
                        # present in SRC but not in TGT
        print("Data presnt in SRC but not in TGT")
        print(records_present_in_df1_not_in_df2)
                        # records_present_in_df1_not_in_df2.to_excel('diffrance.xlsx',sheet_name='difference')
                        # output = df1.copy()
        file_name = settings.DATA_DIR/'output.xlsx'
        with pd.ExcelWriter(file_name) as writer:
                                        df1.to_excel(writer, sheet_name='SRC_data', index=False)
                                        df2.to_excel(writer, sheet_name='TARGET', index=False)
                                        records_present_in_df1_not_in_df2.to_excel(
                                            writer, sheet_name='DIFF Record', index=False)

        win32api.MessageBox(
                            0, 'You can download the comparison report by clicking on download button', '', 0x00001000)
    context = {'file_d': 'Output.xlsx'}
    return render(request, 'Excel_temp.html', context)

# sql db
def sql(request): 
    datadict = {}
    global connection
    global connection1
    if request.method == 'POST' and 'htmlsubmitbutton1' in request.POST:
        List_type = []
        List_type1 = []
        hostid = request.POST.get('ip')
        sid = request.POST.get('sid')
        username = request.POST.get('username')
        pswd = request.POST.get('password')

        hostid1 = request.POST.get('ip1')
        sid1 = request.POST.get('sid1')
        username1 = request.POST.get('username1')
        pswd1 = request.POST.get('password1')
        # mssql credentials
        m_database = request.POST.get('m_database')
        m_host = request.POST.get('m_host')
        m_port = request.POST.get('m_port')
        m_user = request.POST.get('m_uid')
        m_pass = request.POST.get('m_pass')

        m_database1 = request.POST.get('m_database1')
        m_host1 = request.POST.get('m_host1')
        m_port1 = request.POST.get('m_port1')
        m_user1 = request.POST.get('m_uid1')
        m_pass1 = request.POST.get('m_pass1')

        # DB2 credentials
        # m_database = request.POST.get('db2_host')
        # m_host = request.POST.get('db2_port')
        # m_port = request.POST.get('db2_db')
        # m_user = request.POST.get('db2_uid')
        # m_pass = request.POST.get('db2_pass')

        # m_database1 = request.POST.get('m_database1')
        # m_host1 = request.POST.get('m_host1')
        # m_port1 = request.POST.get('m_port1')
        # m_user1 = request.POST.get('m_uid1')
        # m_pass1 = request.POST.get('m_pass1')

        print("   ---  *  "*6)
        print("first db detail")
        print(
            f"username :{m_user} password: {m_pass} database : {m_database} ")
        print("   ---    "*6)
        print("secound db detail")
        print(
            f"username :{m_user1} password: {m_pass1} database : {m_database1} ")
        print("   ---  *  "*6)
        # print(f"username :{m_user} password: {m_pass} server name : {m_server} and Database:{m_database} ")

        try:
            
            if request.POST.get('FormSelect') == 'ORCL':
                print("source orcl")
                # source oracle db connection
                dsn_tns = cx_Oracle.makedsn(hostid, '1521', service_name=sid)
                
                connection = cx_Oracle.connect(
                    user=username, password=pswd, dsn=dsn_tns)
                Data = pd.read_sql(f"SELECT TNAME FROM tab  ",connection, index_col=['TNAME'])
                df = pd.DataFrame(Data).index
                List_type = list(df)
                print("___________________________________***********___________________________")
                print(List_type)
                # datadict = {"Record1": List_type}
            elif request.POST.get('FormSelect') == 'MSSQL':
                print("source mssql")
                # MSSQL db1
                # connection = pymssql.connect(host=m_host,user=m_user, password=m_pass, database=m_database)
                # cursor = connection.cursor(as_dict=True)
                connection = pymssql.connect(host='USAZDCSMAXDB2.delphiprd.am.joneslanglasalle.com:1433/idlmxm1;',user='maximo', password='maximo', database='idlmxm1')
                cursor = connection.cursor(as_dict=True)

                # cursor.execute(
                #     "SELECT TABLE_NAME FROM [idlmxm1].INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
                cursor.execute(
                    "SELECT TABLE_NAME FROM [idlmxm1].INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
                
                # my_list = []
                i = 1
                while True:
                    data = cursor.fetchone()
                    i += 1
                    if data:
                        tablename = data.get('TABLE_NAME')
                        List_type.append(tablename)
                    else:
                        break
                    print(List_type)
                    print("done", len(List_type))
                    # datadict = {"Record1": list(List_type)}
            else:
                win32api.MessageBox(
                    0, 'Please select Source Database', '', 0x00001000)

            if request.POST.get('exampleFormControlSelect1') == 'orcl1':
                print("target orcl")
                # target oracle db connection
                dsn_tns1 = cx_Oracle.makedsn(
                    hostid1, '1521', service_name=sid1)
                
                connection1 = cx_Oracle.connect(
                    user=username1, password=pswd1, dsn=dsn_tns1)
                Data1 = pd.read_sql(f"SELECT TNAME FROM tab  ",
                                    connection1, index_col=['TNAME'])
                df1 = pd.DataFrame(Data1).index
                List_type1 = list(df1)
                print("___________________________________***********___________________________")
                print(List_type1)
                datadict = {"record2": List_type1}
            elif request.POST.get('exampleFormControlSelect1') == 'mssql1':
                print("target mssql")
                # MSSQL db2
                # connection1 = pymssql.connect(host=m_host1,
                #                         user=m_user1, password=m_pass1, database=m_database1)
                # cursor1 = connection1.cursor(as_dict=True)
                connection1 = pymssql.connect(host='USAZDCSMAXDB2.delphiprd.am.joneslanglasalle.com:1433/idlmxm1;',user='maximo', password='maximo', database='idlmxm1')
                cursor1 = connection1.cursor(as_dict=True)
                cursor1.execute(
                    "SELECT TABLE_NAME FROM [idlmxm1].INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
                # my_list1 = []
                i = 1
                while True:
                    data1 = cursor1.fetchone()
                    i += 1
                    if data1:
                        tablename = data1.get('TABLE_NAME')
                        List_type1.append(tablename)
                    else:
                        break
                    print(List_type1)
                    print("done", len(List_type1))
                    # datadict = {"record2": list(List_type1)}

            # elif request.POST.get('FormSelect')=='DB2' and request.POST.get('exampleFormControlSelect1')=='db21':
            #     print("Creating source DB2 connection.......")
            #     conn_string = "DATABASE=bludb;HOSTNAME=yourhostname;PORT=<port>;PROTOCOL=TCPIP;UID=<userId>;PWD=<password>;SECURITY=SSL"

            #     conn = ibm_db.connect(conn_string,"","")
            #     if conn:
            #         print("Connection ...... [SUCCESS]")
            #     else:
            #         print("Connection ...... [FAILURE]")

            #     print("while complited")
            #     cursor.close()
            #     win32api.MessageBox(0,'You have connected to '+request.POST.get('FormSelect')+' database successfully!','', 0x00001000)
            #     datadict={"Record":list(my_list),"table2":my_list1}
            else:
                win32api.MessageBox(0, 'Please select Target Database', '', 0x00001000)
            datadict = {"Record1": list(List_type),"record2": list(List_type1)}

        except Exception as e:
            win32api.MessageBox(0, 'Connection Failed!', '', 0x00001000)
            print(e)
        else:
            # win32api.MessageBox(0,'Database Connection Succeed','', 0x00001000)
            Trans_msg = "Database Connection Succeed"
            # datadict={"success_msg":Trans_msg}

    if request.method == 'POST' and 'htmlsubmitbutton2' in request.POST:
        SRC_TABLE = request.POST.get('dropdown1')
        TGT_TABLE = request.POST.get('dropdown2')

        dio = pd.read_sql(f'select * from SRC.{SRC_TABLE}', connection)
        Excel1 = pd.DataFrame(dio)

        # print(Excel1)
        # del Excel1['rowstamp']
        Excel1.to_excel('Excel1.xlsx', index=False)
    
        data = pd.read_sql(f'select *  from TGT.{TGT_TABLE}', connection1)
        Excel2 = pd.DataFrame(data)

        # Excel2=Excel2.set_index(Excel2.columns[0])

        # del Excel2['rowstamp_T']
        print("Rowstamp Was Deleted")
        Excel2.to_excel('Excel2.xlsx', index=False)
        datadict = {"data": data}
        print(data)

        print("READING DATA FRAME ONE\n"*3)

        df1 = pd.read_excel('Excel1.xlsx').astype(str).replace(
                'nan', '')  # Fisrt Table Record DataFrame SRC DB
        print("READING DATA FRAME TWO\n"*3)

        df2 = pd.read_excel('Excel2.xlsx').astype(str).replace(
                'nan', '')  # Secound Table Record DataFrame TGT DB

        print("length of df1 :  ",len(df1.columns))
        print("length of df2 :  ",len(df2.columns))            
        # data comparison business logic
        print("COMPARION START\n"*2)
        compare = datacompy.Compare(
                df1, df2, join_columns=f'{df1.columns[0]}', df1_name='SRC_DATA',
                df2_name='TGT_DATA')
        text_report = compare.report()
        file_report_txt = settings.DATA_DIR/'TableReprort.txt'
        report_file = open(file_report_txt, 'w', encoding="utf-8")
        report_file.write(text_report)
        report_file.close()

        print("comparison END")
            # EXCEL DIFFERENCE

        df1.rename(columns=lambda x: x + '_S')
        df2.rename(columns=lambda x: x + '_T', inplace=True)
        print("DF RENAMEING OK",len(df1.columns))
        print("JOING/MEging STRATED")
        
        list1 = []
        list2 = []
        for x in df1.columns:
            # print("hi",x)
            new_x=x.replace(x,x+"_T")
            # print("new x : ",new_x)
            for y in df2.columns:
                # print("bye",y)
                
                if new_x==y:
                    # print("col1 : ",x)
                    
                    # print(df_join)
                    # print("x :",df1)
                    # print("value",x)
                    list1.append(x)
                    list2.append(y)
                    df_join = df1.merge(right=df2,
                                            left_on=list1,
                                            right_on=list2,
                                            how='left')
                    # print("list 1 :  ",list1)
                    # sorting the excel record on matching (JOIN)
        print("list 1 : ",list1[0])
        print("list 2 : ",list2[0])
        # records_present_in_df1_not_in_df2 = df_join.loc[df_join[list2], list1]
        # records_present_in_df2_not_in_df1 = df_join.loc[df_join[list1], list2]
        records_present_in_df1_not_in_df2 = df_join.loc[df_join[list2].isnull().all(axis=1), list1]
        # df_join = df1.merge(right=df2,
        #                         left_on=df1.columns.to_list(),
        #                         right_on=df2.columns.to_list(),
        #                         how='outer')
        #     # sorting the excel record on matching (JOIN)
        # print("merge End",df2.columns)
        # print("joint",df2.columns.to_list())
        # records_present_in_df1_not_in_df2 = df_join.loc[df_join[df2.columns.to_list(
        #     )].isnull().all(axis=1), df1.columns.to_list()]
        # records_present_in_df2_not_in_df1 = df_join.loc[df_join[df1.columns.to_list(
        #     )].isnull().all(axis=1), df2.columns.to_list()]
            # present in SRC but not in TGT


        print(records_present_in_df1_not_in_df2)
            # records_present_in_df1_not_in_df2.to_excel('diffrance.xlsx',sheet_name='differance')
            # output = df1.copy()
        file_name = settings.DATA_DIR/'TABLE_DIFF.xlsx'
        with pd.ExcelWriter(file_name) as writer:
                df1.to_excel(writer, sheet_name='SRC_data', index=False)
                df2.to_excel(writer, sheet_name='TARGET', index=False)
                records_present_in_df1_not_in_df2.to_excel(
                    writer, sheet_name='DIFF Record', index=False)
        win32api.MessageBox(0, 'Compared Successfully! Now you can download the report by clicking on download button', '', 0x00001000)
        # context = {'file_d':'DifferanceOutput.xlsx'}
        datadict = {"data": data, 'file_data': 'DifferenceOutput.xlsx'}

    return render(request, 'PostValid.html',datadict)