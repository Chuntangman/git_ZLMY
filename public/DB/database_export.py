import pyodbc
import json
import os
from db_config import execute_query

def connect_to_database():
    """连接到SQL Server数据库
    Returns:
        pyodbc.Connection: 数据库连接对象
    """
    conn_str = (
        "DRIVER={SQL Server};"
        "SERVER=localhost;"
        "DATABASE=智理名岩数据库;"
        "UID=906898206;"
        "PWD=6912190819"
    )
    return pyodbc.connect(conn_str)

def read_rock_samples(conn):
    """从数据库读取岩石标本表数据
    Args:
        conn (pyodbc.Connection): 数据库连接对象
    Returns:
        list: 包含所有岩石标本数据的列表
    """
    cursor = conn.cursor()
    query = "SELECT * FROM 岩石标本"
    cursor.execute(query)
    
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        result = {}
        for i, value in enumerate(row):
            result[columns[i]] = value
        results.append(result)
    
    return results

def update_rock_samples_json(rock_samples):
    """更新岩石标本数据到NewRegion3D.json文件
    Args:
        rock_samples (list): 岩石标本数据列表
    
    功能：
    - 读取NewRegion3D.json文件
    - 根据ID更新features中的properties
    - 保存更新后的数据
    """
    json_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                 'mock-models', 'NewRegion3D.json')
    
    # 读取原始JSON文件
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 创建ID到样本数据的映射
    sample_map = {sample['ID']: sample for sample in rock_samples}
    
    # 更新features中的properties
    for feature in data['features']:
        number = feature['properties']['Number']
        if number in sample_map:
            sample_data = sample_map[number]
            for key, value in sample_data.items():
                if key != 'ID':  # ID已经作为Number存在，不需要重复添加
                    feature['properties'][key] = value if value is not None else ""
    
    # 保存更新后的JSON文件
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def export_relations():
    """导出关联关系数据到relations.json
    
    功能：
    - 从关联关系表查询数据
    - 导出到relations.json文件
    - 包含关联类型、实体ID和关联程度等信息
    """
    query = """
    SELECT [关联类型], [关联实体ID1],[关联实体ID2], [关联程度], [url]
    FROM [关联关系]
    """
    
    try:
        results = execute_query(query)
        output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                 'mock-models', 'relations.json')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print(f"关联关系数据已成功导出到: {output_path}")
        
    except Exception as e:
        print(f"导出关联关系数据时出错: {str(e)}")

def export_3d_models():
    """导出三维模型数据到Bottom_sidebar.json
    
    功能：
    - 从三维模型表查询数据
    - 导出到Bottom_sidebar.json文件
    - 包含模型的基本信息和URL等
    """
    query = """
    SELECT *
    FROM [三维模型]
    """
    
    try:
        results = execute_query(query)
        output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                 'mock-models', 'Bottom_sidebar.json')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print(f"三维模型数据已成功导出到: {output_path}")
        
    except Exception as e:
        print(f"导出三维模型数据时出错: {str(e)}")

def main():
    """主函数：执行所有数据导出任务
    
    执行顺序：
    1. 更新岩石标本数据到NewRegion3D.json
    2. 导出关联关系数据到relations.json
    3. 导出三维模型数据到Bottom_sidebar.json
    """
    try:
        # 连接数据库并更新岩石标本数据
        conn = connect_to_database()
        print("成功连接到数据库")
        
        rock_samples = read_rock_samples(conn)
        print(f"成功读取 {len(rock_samples)} 条岩石标本数据")
        
        update_rock_samples_json(rock_samples)
        print("成功更新岩石标本数据到NewRegion3D.json")
        
        # 导出关联关系和三维模型数据
        export_relations()
        export_3d_models()
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()
            print("数据库连接已关闭")

if __name__ == "__main__":
    main() 