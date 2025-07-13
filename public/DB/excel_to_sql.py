import pandas as pd
import pyodbc
import os
from tkinter import Tk, filedialog
import numpy as np

def get_sql_type(dtype, column_name):
    """根据pandas的数据类型确定SQL Server的数据类型"""
    if column_name.upper() == 'ID':
        return 'INT'  # ID列强制使用INT类型
    if 'int' in str(dtype):
        return 'INT'
    elif 'float' in str(dtype):
        return 'FLOAT'
    elif 'datetime' in str(dtype):
        return 'DATETIME'
    else:
        return 'NVARCHAR(255)'

def sanitize_table_name(name):
    """处理表名，确保符合SQL Server命名规则"""
    # 如果表名以数字开头，添加前缀
    if name[0].isdigit():
        name = 'Table_' + name
    # 替换不允许的字符
    name = name.replace('.', '_').replace(' ', '_')
    return name

def create_table_query(df, table_name):
    """生成创建表的SQL语句"""
    columns = []
    for col, dtype in df.dtypes.items():
        sql_type = get_sql_type(dtype, col)
        # 如果列名是'ID'，设置为主键
        if col.upper() == 'ID':
            columns.append(f"[{col}] {sql_type} PRIMARY KEY")
        else:
            columns.append(f"[{col}] {sql_type}")
    
    return f"""
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = '{table_name}')
    CREATE TABLE {table_name} (
        {', '.join(columns)}
    )
    """

def process_excel_file(file_path, conn, cursor):
    """处理单个Excel文件"""
    # 获取文件名（不包含扩展名）作为表名
    table_name = os.path.splitext(os.path.basename(file_path))[0]
    table_name = sanitize_table_name(table_name)
    
    try:
        # 读取Excel文件，不自动推断数据类型
        df = pd.read_excel(file_path, dtype=str)
        
        # 特殊处理ID列
        if 'ID' in df.columns:
            # 将ID列转换为整数
            df['ID'] = pd.to_numeric(df['ID'], errors='coerce').fillna(0).astype(int)
        
        # 创建表
        create_query = create_table_query(df, table_name)
        cursor.execute(create_query)

        # 准备插入数据
        # 将所有数据转换为字符串，处理nan值
        df = df.replace({np.nan: None})
        
        # 构建插入语句
        columns = [f"[{col}]" for col in df.columns]
        placeholders = ['?' for _ in df.columns]
        insert_query = f"""
        INSERT INTO {table_name} ({', '.join(columns)})
        VALUES ({', '.join(placeholders)})
        """

        # 批量插入数据
        for _, row in df.iterrows():
            cursor.execute(insert_query, tuple(row))

        print(f"成功将Excel文件 '{os.path.basename(file_path)}' 导入到数据库表 '{table_name}'")
        return True
        
    except Exception as e:
        print(f"处理文件 '{os.path.basename(file_path)}' 时发生错误: {str(e)}")
        return False

def excel_to_sql():
    # 创建tkinter根窗口（但不显示）
    root = Tk()
    root.withdraw()

    # 打开文件选择对话框（支持多选）
    file_paths = filedialog.askopenfilenames(
        title='选择Excel文件（可多选）',
        filetypes=[('Excel files', '*.xlsx *.xls')]
    )

    if not file_paths:
        print("未选择文件")
        return

    try:
        # 数据库连接配置
        conn_str = (
            "DRIVER={SQL Server};"
            "SERVER=localhost;"
            "DATABASE=智理名岩数据库;"
            "UID=906898206;"
            "PWD=6912190819"
        )

        # 连接数据库
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # 处理每个选中的文件
        success_count = 0
        total_files = len(file_paths)

        for file_path in file_paths:
            if process_excel_file(file_path, conn, cursor):
                success_count += 1
            
            # 提交事务
            conn.commit()

        # 显示总体处理结果
        print(f"\n处理完成！成功导入 {success_count}/{total_files} 个文件。")

    except Exception as e:
        print(f"连接数据库时发生错误: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    excel_to_sql() 