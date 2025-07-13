import pyodbc
from contextlib import contextmanager
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 数据库连接配置
DB_CONFIG = {
    "driver": "SQL Server",
    "server": "localhost",
    "database": "智理名岩数据库",
    "trusted_connection": "yes",  # 使用Windows身份验证
    "charset": "UTF-8"
}

def get_connection_string():
    """获取数据库连接字符串"""
    return (
        f"DRIVER={{{DB_CONFIG['driver']}}};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"Trusted_Connection={DB_CONFIG['trusted_connection']};"
        f"charset={DB_CONFIG['charset']}"
    )

@contextmanager
def get_db_connection():
    """获取数据库连接（上下文管理器）"""
    conn = None
    try:
        conn_str = get_connection_string()
        logger.debug(f"Attempting to connect with connection string: {conn_str}")
        conn = pyodbc.connect(conn_str)
        logger.debug("Database connection established successfully")
        yield conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed")

def execute_query(query, params=None):
    """执行查询并返回结果"""
    try:
        logger.debug(f"Executing query: {query}")
        if params:
            logger.debug(f"With parameters: {params}")
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # 获取列名
            if not cursor.description:
                logger.warning("Query returned no results")
                return []
                
            columns = [column[0] for column in cursor.description]
            logger.debug(f"Query columns: {columns}")
            
            # 获取结果
            results = []
            for row in cursor.fetchall():
                result = {}
                for i, value in enumerate(row):
                    result[columns[i]] = value
                results.append(result)
            
            logger.debug(f"Query returned {len(results)} results")
            return results
    except Exception as e:
        logger.error(f"Query execution error: {str(e)}")
        raise

def execute_update(query, params=None):
    """执行更新操作（INSERT, UPDATE, DELETE）
    
    Args:
        query (str): SQL更新语句
        params (tuple, optional): 查询参数
    
    Returns:
        int: 受影响的行数
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor.rowcount

def test_connection():
    """测试数据库连接"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # 测试查询
            cursor.execute("SELECT TOP 1 编号 FROM 岩石样品")
            result = cursor.fetchone()
            if result:
                logger.info(f"Connection test successful. Sample ID: {result[0]}")
            return True
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        return False

# 使用示例
if __name__ == "__main__":
    # 测试连接
    if test_connection():
        print("数据库连接测试成功！")
        
        # 测试岩石样品查询
        try:
            query = "SELECT TOP 1 * FROM 岩石样品 WHERE 编号 = ?"
            results = execute_query(query, ("长7-2",))
            print("\n测试查询长7-2的数据:")
            for result in results:
                print(result)
        except Exception as e:
            print(f"查询测试失败: {str(e)}")
    else:
        print("数据库连接测试失败！") 