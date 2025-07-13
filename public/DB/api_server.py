from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from db_config import execute_query
import base64
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置为具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/3d-models")
async def get_3d_models():
    try:
        logger.debug("Fetching all 3D models")
        query = """
        SELECT 
            ID,
            地理地名,
            文字介绍,
            大地坐标X,
            大地坐标Y,
            盆地,
            所处方位,
            URL
        FROM 三维模型
        """
        results = execute_query(query)
        logger.debug(f"Found {len(results)} 3D models")
        return results
    except Exception as e:
        logger.error(f"Error in get_3d_models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/3d-models/{model_id}")
async def get_3d_model(model_id: int):
    try:
        logger.debug(f"Fetching 3D model with ID: {model_id}")
        query = """
        SELECT 
            ID,
            地理地名,
            文字介绍,
            大地坐标X,
            大地坐标Y,
            盆地,
            所处方位,
            URL
        FROM 三维模型
        WHERE ID = ?
        """
        results = execute_query(query, (model_id,))
        logger.debug(f"Query results: {results}")
        
        if not results:
            logger.warning(f"No 3D model found for ID: {model_id}")
            raise HTTPException(status_code=404, detail=f"3D model not found: {model_id}")
            
        return results[0]
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in get_3d_model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected server error: {str(e)}")

@app.get("/api/relations/{entity_id}")
async def get_relations(entity_id: str):
    try:
        logger.debug(f"Fetching relations for entity_id: {entity_id}")
        # 首先查询关联关系
        query = """
        SELECT 
            关联关系.ID,
            关联关系.关联类型,
            关联关系.关联实体ID1,
            关联关系.关联实体ID2,
            关联关系.关联程度,
            关联关系.文件,
            岩石样品1.名称 AS 实体1名称,
            岩石样品2.名称 AS 实体2名称
        FROM 关联关系
        LEFT JOIN 岩石样品 AS 岩石样品1 ON 关联关系.关联实体ID1 = 岩石样品1.编号
        LEFT JOIN 岩石样品 AS 岩石样品2 ON 关联关系.关联实体ID2 = 岩石样品2.编号
        WHERE 关联实体ID1 = ? OR 关联实体ID2 = ?
        ORDER BY 关联程度 DESC
        """
        results = execute_query(query, (entity_id, entity_id))
        logger.debug(f"Found {len(results)} relations")
        
        # 处理文件路径，添加url字段
        for result in results:
            if result.get('文件'):
                result['url'] = f"/mock-models/{result['文件']}"
            else:
                result['url'] = None
                
        return results
    except Exception as e:
        logger.error(f"Error in get_relations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rock-sample/{sample_id}")
async def get_rock_sample_details(sample_id: str):
    try:
        logger.debug(f"Fetching rock sample details for sample_id: {sample_id}")
        # 查询岩石样品基本信息
        sample_query = """
        SELECT 
            编号,
            名称,
            盆地,
            来源,
            层位,
            岩性,  -- 添加更多可能的字段
            描述,
            采样位置,
            采样时间
        FROM 岩石样品
        WHERE 编号 = ?
        """
        try:
            sample_results = execute_query(sample_query, (sample_id,))
            logger.debug(f"Sample query executed. Results: {sample_results}")
        except Exception as e:
            logger.error(f"Error executing sample query: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error in sample query: {str(e)}")
        
        if not sample_results:
            logger.warning(f"No sample found for ID: {sample_id}")
            raise HTTPException(status_code=404, detail=f"Sample not found: {sample_id}")
            
        sample_info = sample_results[0]
        logger.debug(f"Sample info retrieved: {sample_info}")
        
        # 查询相关的多媒体文件
        media_query = """
        SELECT 
            ID,
            文件,
            文件类型,  -- 添加文件类型字段
            描述      -- 添加描述字段
        FROM 多媒体文件
        WHERE 关联id = ? AND 关联类型 = '岩石样品'
        """
        try:
            media_results = execute_query(media_query, (sample_id,))
            logger.debug(f"Media query executed. Found {len(media_results)} results")
            
            # 处理二进制图片数据
            media_files = []
            for media in media_results:
                try:
                    if media.get('文件'):
                        # 将二进制数据转换为base64字符串
                        binary_data = media['文件']
                        if isinstance(binary_data, memoryview):
                            binary_data = binary_data.tobytes()
                        base64_data = base64.b64encode(binary_data).decode('utf-8')
                        media_files.append({
                            'id': media['ID'],
                            'data': f"data:image/png;base64,{base64_data}",
                            'type': media.get('文件类型'),
                            'description': media.get('描述')
                        })
                        logger.debug(f"Successfully processed media file ID: {media['ID']}")
                except Exception as e:
                    logger.error(f"Error processing media file {media.get('ID', 'unknown')}: {str(e)}")
                    continue
            
            # 组合返回数据
            response_data = {
                **sample_info,
                'media_files': media_files
            }
            logger.debug(f"Returning response data with {len(media_files)} media files")
            
            return response_data
        except Exception as e:
            logger.error(f"Error executing media query: {str(e)}")
            # 如果多媒体查询失败，我们仍然返回基本信息
            return {
                **sample_info,
                'media_files': []
            }
    except HTTPException as he:
        # 重新抛出HTTP异常
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in get_rock_sample_details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected server error: {str(e)}")

@app.get("/api/thin-section/{sample_id}")
async def get_thin_section_details(sample_id: str):
    try:
        logger.debug(f"Fetching thin section details for sample_id: {sample_id}")
        # 查询薄片鉴定报告基本信息
        report_query = """
        SELECT 
            编号,
            岩类,
            成分,
            粒度,
            特殊物质,
            特殊结构,
            颜色,
            照片,
            磨圆,
            面孔率,
            分选,
            杂基,
            岩屑含量,
            长石含量,
            石英含量
        FROM 薄片鉴定报告
        WHERE 编号 = ?
        """
        report_results = execute_query(report_query, (sample_id,))
        logger.debug(f"Report query results: {report_results}")
        
        if not report_results:
            logger.warning(f"No thin section report found for ID: {sample_id}")
            raise HTTPException(status_code=404, detail=f"Thin section report not found: {sample_id}")
            
        report_info = report_results[0]
        
        # 查询相关的多媒体文件
        media_query = """
        SELECT 
            ID,
            文件
        FROM 多媒体文件
        WHERE 关联id = ? AND 关联类型 = '薄片鉴定报告'
        """
        try:
            media_results = execute_query(media_query, (sample_id,))
            logger.debug(f"Media query executed. Found {len(media_results)} results")
            
            # 处理二进制图片数据
            media_files = []
            for media in media_results:
                try:
                    if media.get('文件'):
                        # 将二进制数据转换为base64字符串
                        binary_data = media['文件']
                        if isinstance(binary_data, memoryview):
                            binary_data = binary_data.tobytes()
                        base64_data = base64.b64encode(binary_data).decode('utf-8')
                        media_files.append({
                            'id': media['ID'],
                            'data': f"data:image/png;base64,{base64_data}"
                        })
                        logger.debug(f"Successfully processed media file ID: {media['ID']}")
                except Exception as e:
                    logger.error(f"Error processing media file {media.get('ID', 'unknown')}: {str(e)}")
                    continue
            
            # 组合返回数据
            response_data = {
                **report_info,
                'media_files': media_files
            }
            logger.debug(f"Returning response data with {len(media_files)} media files")
            
            return response_data
        except Exception as e:
            logger.error(f"Error executing media query: {str(e)}")
            # 如果多媒体查询失败，我们仍然返回基本信息
            return {
                **report_info,
                'media_files': []
            }
            
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in get_thin_section_details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected server error: {str(e)}")

@app.get("/api/xrf-test/{sample_id}")
async def get_xrf_test_results(sample_id: str):
    try:
        logger.debug(f"Fetching XRF test results for sample_id: {sample_id}")
        # 移除输入sample_id中的空格，并构建两个可能的查询值
        sample_id_no_space = sample_id.replace(" ", "")
        sample_id_with_space = " ".join(sample_id_no_space[i:i+1] for i in range(len(sample_id_no_space)))
        
        query = """
        SELECT 
            层位,
            野外定名,
            Si,
            Mg,
            Al,
            K,
            Ca,
            Fe,
            Ba
        FROM XRF测试结果
        WHERE 编号 = ? OR 编号 = ?
        """
        results = execute_query(query, (sample_id, sample_id_with_space))
        logger.debug(f"XRF query results: {results}")
        
        if not results:
            # 如果还是没有结果，尝试用不带空格的版本再查一次
            query = """
            SELECT 
                层位,
                野外定名,
                Si,
                Mg,
                Al,
                K,
                Ca,
                Fe,
                Ba
            FROM XRF测试结果
            WHERE REPLACE(编号, ' ', '') = ?
            """
            results = execute_query(query, (sample_id_no_space,))
            logger.debug(f"XRF query results with no space: {results}")
            
        if not results:
            logger.warning(f"No XRF test results found for ID: {sample_id}")
            raise HTTPException(status_code=404, detail=f"XRF test results not found: {sample_id}")
            
        return results[0]
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in get_xrf_test_results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected server error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000) 