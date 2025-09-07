# my_ml_backend.py
import os
import shutil
from PIL import Image
import logging
import base64
from label_studio_ml.model import LabelStudioMLBase
from volcenginesdkarkruntime import Ark

# 配置日志，输出到文件
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='doubao_backend.log'  # 指定日志文件名称
)
logger = logging.getLogger(__name__)

class DoubaoVisionAPI(LabelStudioMLBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.local_config = {
            'path': os.getenv('LOCAL_STORAGE_PATH', 'D:/datasets'),  # 本地存储路径
            'base_url': os.getenv('LOCAL_BASE_URL', 'http://localhost:8000'),
            'region': os.getenv('TOS_REGION', 'cn-beijing'),
            'target_size': 300 * 1024  # 压缩目标
        }

        self.client = Ark(
            api_key=os.environ.get("ARK_API_KEY"),
            region='cn-beijing',
            timeout=120
        )
        self.url = "https://ark-project.tos-cn-beijing.volces.com"
    
    # def _check_tos_bucket(self):
    #     """检查TOS存储桶是否存在"""
    #     tos_client = tos.TosClientV2(
    #         os.getenv('VOLC_ACCESSKEY'),
    #         os.getenv('VOLC_SECRETKEY'),
    #         self.tos_config['endpoint'],
    #         self.tos_config['region']
    #     )
        
    #     try:
    #         tos_client.head_bucket(self.tos_config['bucket'])
    #     except tos.exceptions.TosServerError as e:
    #         if e.status_code == 404:
    #             raise RuntimeError(f"存储桶 {self.tos_config['bucket']} 不存在，请先通过控制台创建")
    #         raise
    
    def get_model_version(self):
        return "Doubao-1.5-Vison-Pro"

    # 将指定路径图片转为Base64编码
    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
        

    def _process_image(self, image_url, task_id):
        """图像处理流水线"""
        try:
            # 添加空值检查
            if not image_url:
                raise ValueError(f"Empty image URL for task {task_id}")
            # img_url转为本地路径
            image_path = image_url.replace(self.local_config['base_url'], self.local_config['path'])
            logger.info(f"Processing image path: {image_path}")  # 添加路径日志
            
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Local image not found: {image_path}")
            
            # 压缩图片
            processed_dir = os.path.join(self.local_config['path'], 'processed').replace('\\', '/')
            if not os.path.exists(processed_dir):
                os.makedirs(processed_dir)
            output_path = os.path.join(processed_dir, f"temp_{task_id}.jpeg").replace('\\', '/')
            self._compress_image(image_path, output_path)
            
            # 转为base64编码
            base64_image = self.encode_image(output_path)
            return base64_image
            
        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            raise

    def _compress_image(self, input_path, output_path):
        try:
            current_size = os.path.getsize(input_path)
            if current_size <= self.local_config['target_size']:
                shutil.copy(input_path, output_path)
                return

            img = Image.open(input_path)
            # 处理可能存在的透明度通道问题
            if img.mode in ('RGBA', 'LA'):
                img = img.convert('RGB')
            
            quality = 95  # 初始质量设为最高
            min_quality = 10
            temp_path = output_path.rsplit('.', 1)[0] + "_temp.jpg"

            while quality >= min_quality:
                try:
                # 显式指定JPEG格式
                    img.save(temp_path, format='JPEG', quality=quality, 
                            optimize=True, subsampling=0 if quality >= 90 else 2)
                except IOError:
                    # 处理渐进式JPEG可能出现的错误
                    img.save(temp_path, format='JPEG', quality=quality, 
                            optimize=False, subsampling=0 if quality >= 90 else 2)
                
                new_size = os.path.getsize(temp_path)
                if new_size <= self.local_config['target_size']:
                    break
                    
                oversize_ratio = (new_size - self.local_config['target_size']) / self.local_config['target_size']
                quality_step = max(int(oversize_ratio * 20), 1)
                quality = max(quality - quality_step, min_quality)

            # 重命名临时文件到目标路径
            if os.path.exists(output_path):
                os.remove(output_path)
            os.rename(temp_path, output_path)
            img.close()

        except Exception as e:
            logger.error(f"Image compression failed: {str(e)}")
            raise
        finally:
            # 确保清理临时文件
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception as e:
                    logger.debug(f"Clean temp file failed: {str(e)}")

    def predict(self, tasks, **kwargs):
        """核心预测逻辑"""
        predictions = []
        for task in tasks:
            try:
                # 从Label Studio获取输入
                image_url = task['data'].get('image')
                question = task['data'].get('question', "请描述这张图片的内容")
                task_id = task['id']

                # 添加详细日志记录
                logger.info(f"Processing task {task_id} with image: {image_url[:80] if image_url else 'None'}")
                # 处理图片并获取访问URL
                base64_image = self._process_image(image_url, task_id)
              
                # 调用大模型API
                response = self.client.chat.completions.create(
                    model="doubao-1-5-vision-pro-250328",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": question},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    }]
                )

                # 解析响应结果
                result_text = response.choices[0].message.content
                
                # 构建Label Studio兼容的预测结果
                predictions.append({
                    "result": [{
                        "type": "textarea",
                        "from_name": "model_description",
                        "to_name": "image_display",
                        "value": {"text": result_text,
                                  "model_type":"ImageModel"}
                    }],
                    "model_version": "Doubao-1.5-Vison-Pro"  # 添加模型版本标识
                })
                
            except Exception as e:
                logger.error(f"Prediction failed for task {task_id}: {str(e)}")
                # 保持错误时的数据结构一致
                predictions.append({
                    "result": [{
                        "from_name": "model_description",
                        "to_name": "image_display",
                        "type": "textarea",
                        "value": {"text": "ERROR: 预测失败",
                                  "model_type":"ImageModel"}
                    }],
                    "model_version": "Doubao-1.5-Vison-Pro"  # 添加模型版本标识
                })

        return predictions  # 包装为字典返回