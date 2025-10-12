import os
import yaml
import cv2
import shutil
from ultralytics import YOLO
from sklearn.model_selection import train_test_split
import albumentations as A
from albumentations.pytorch import ToTensorV2

class AdultAnimalTrainer:
    def __init__(self, data_path):
        self.data_path = data_path
        self.setup_directories()
        
    def setup_directories(self):
        """创建必要的目录结构"""
        dirs = [
            'images/train',
            'images/val', 
            'labels/train',
            'labels/val'
        ]
        
        for dir_path in dirs:
            os.makedirs(os.path.join(self.data_path, dir_path), exist_ok=True)
    
    def create_data_yaml(self):
        """创建数据集配置文件 - 只包含成年动物"""
        data_config = {
            'path': self.data_path,
            'train': 'images/train',
            'val': 'images/val',
            'nc': 2,  # 只识别2种成年动物
            'names': [
                '垂耳兔_成年',
                '白犀牛_成年'
            ]
        }
        
        with open(os.path.join(self.data_path, 'data.yaml'), 'w', encoding='utf-8') as f:
            yaml.dump(data_config, f, allow_unicode=True)
        print("创建数据集配置文件完成，只包含成年动物")
    
    def collect_adult_images(self):
        """收集所有成年动物图像"""
        adult_images = []
        
        # 遍历每种动物文件夹
        for animal in ['垂耳兔', '白犀牛']:
            adult_dir = os.path.join(self.data_path, animal, '成年')
            if os.path.exists(adult_dir):
                for file in os.listdir(adult_dir):
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        adult_images.append({
                            'path': os.path.join(adult_dir, file),
                            'animal': animal,
                            'class_id': 0 if animal == '垂耳兔' else 1  # 垂耳兔=0, 白犀牛=1
                        })
        
        print(f"找到 {len(adult_images)} 张成年动物图像")
        return adult_images
    
    def create_yolo_labels(self, image_info, label_path):
        """创建YOLO格式的标签文件"""
        # 这里需要您提供标注信息
        # 假设您已经用标注工具标注了边界框
        # 格式: class_id x_center y_center width height (归一化坐标)
        
        # 示例：创建一个占位标签（中心点，占图像的50%）
        # 实际使用时请替换为真实的标注数据
        height, width = 640, 640  # 假设图像尺寸
        x_center = 0.5
        y_center = 0.5
        bbox_width = 0.5
        bbox_height = 0.5
        
        with open(label_path, 'w') as f:
            f.write(f"{image_info['class_id']} {x_center} {y_center} {bbox_width} {bbox_height}\n")
    
    def augment_images(self, image_paths, output_dir, num_augmentations=10):
        """数据增强 - 生成更多训练样本"""
        transform = A.Compose([
            A.HorizontalFlip(p=0.5),
            A.RandomBrightnessContrast(p=0.3),
            A.Rotate(limit=15, p=0.4),
            A.GaussianBlur(blur_limit=3, p=0.3),
            A.RandomGamma(p=0.2),
            A.MotionBlur(blur_limit=3, p=0.2),
            A.ISONoise(color_shift=(0.01, 0.05), intensity=(0.1, 0.5), p=0.2),
            A.ToGray(always_apply=True),  # 转换为灰度图
            A.Resize(640, 640),
        ])
        
        for img_info in image_paths:
            image = cv2.imread(img_info['path'])
            if image is None:
                continue
                
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            for i in range(num_augmentations):
                try:
                    # 应用数据增强
                    transformed = transform(image=image)
                    augmented_image = transformed['image']
                    
                    # 保存增强后的图像
                    base_name = os.path.splitext(os.path.basename(img_info['path']))[0]
                    aug_img_path = os.path.join(
                        output_dir, 
                        f"{base_name}_aug_{i}.jpg"
                    )
                    cv2.imwrite(aug_img_path, cv2.cvtColor(augmented_image, cv2.COLOR_RGB2BGR))
                    
                    # 创建对应的标签文件
                    aug_label_path = os.path.join(
                        output_dir.replace('images', 'labels'),
                        f"{base_name}_aug_{i}.txt"
                    )
                    self.create_yolo_labels(img_info, aug_label_path)
                    
                except Exception as e:
                    print(f"数据增强错误: {e}")
                    continue
    
    def prepare_dataset(self):
        """准备训练数据集 - 只使用成年动物"""
        # 收集所有成年动物图像
        adult_images = self.collect_adult_images()
        
        if len(adult_images) == 0:
            print("未找到成年动物图像，请检查目录结构")
            return
        
        # 分割训练集和验证集
        train_data, val_data = train_test_split(
            adult_images, test_size=0.2, random_state=42
        )
        
        print(f"训练集: {len(train_data)} 张, 验证集: {len(val_data)} 张")
        
        # 复制原始图像到训练集和验证集
        for data, split in [(train_data, 'train'), (val_data, 'val')]:
            for img_info in data:
                # 复制图像
                dest_img = os.path.join(
                    self.data_path, 'images', split, 
                    os.path.basename(img_info['path'])
                )
                shutil.copy2(img_info['path'], dest_img)
                
                # 创建对应的标签文件
                label_filename = os.path.splitext(os.path.basename(img_info['path']))[0] + '.txt'
                dest_label = os.path.join(
                    self.data_path, 'labels', split, label_filename
                )
                self.create_yolo_labels(img_info, dest_label)
        
        # 对训练集进行数据增强
        self.augment_images(train_data, os.path.join(self.data_path, 'images/train'))
        
        print("数据集准备完成")
    
    def train_adult_animal_model(self):
        """训练只识别成年动物的模型"""
        # 创建数据配置文件
        self.create_data_yaml()
        
        # 加载预训练模型
        model = YOLO('yolov8n.pt')
        
        # 训练参数配置 - 针对成年动物检测优化
        training_results = model.train(
            data=os.path.join(self.data_path, 'data.yaml'),
            epochs=200,
            imgsz=640,
            batch_size=8,
            device='cpu',  # 使用GPU改为 '0'
            patience=20,
            lr0=0.01,
            save=True,
            exist_ok=True,
            pretrained=True,
            optimizer='Adam',
            amp=True,
            # 针对动物检测的特定参数
            mixup=0.1,           # MixUp数据增强
            copy_paste=0.1,      # 复制粘贴增强
            hsv_h=0.015,         # 色调增强
            hsv_s=0.7,           # 饱和度增强  
            hsv_v=0.4,           # 明度增强
            degrees=10.0,        # 旋转角度
            translate=0.1,       # 平移
            scale=0.5,           # 缩放
            shear=2.0,           # 剪切
            perspective=0.0001,  # 透视变换
            flipud=0.0,          # 上下翻转概率
            fliplr=0.5,          # 左右翻转概率
            mosaic=0.5,          # Mosaic数据增强
        )
        
        return model
    
    def validate_model(self, model_path):
        """验证模型性能"""
        model = YOLO(model_path)
        
        # 在验证集上验证
        results = model.val(
            data=os.path.join(self.data_path, 'data.yaml'),
            split='val',
            save_json=True,
            conf=0.5,
            iou=0.5
        )
        
        print(f"成年动物检测 mAP50: {results.box.map50:.3f}")
        print(f"成年动物检测 mAP50-95: {results.box.map:.3f}")
        
        return results

# 使用示例
if __name__ == "__main__":
    # 初始化训练器
    trainer = AdultAnimalTrainer('/path/to/梦幻西游牧场数据集')
    
    # 准备数据集
    trainer.prepare_dataset()
    
    # 开始训练
    print("开始训练只识别成年动物的模型...")
    model = trainer.train_adult_animal_model()
    
    # 保存最终模型
    model.save('成年动物检测模型.pt')
    print("模型训练完成！")
    
    # 验证模型
    trainer.validate_model('成年动物检测模型.pt')