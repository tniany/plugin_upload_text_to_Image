from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, StarTools
from astrbot.api import logger

import urllib.parse

class MyPlugin(Star):
    def __init__(self, context: Context, config=None):
        super().__init__(context)
        # API配置
        self.api_url = "https://api.suyanw.cn/api/zdytwhc.php"
        self.text_size = 85
        
        # 初始化并发锁
        import asyncio
        self._data_lock = asyncio.Lock()
        
        # 获取数据文件路径
        self.data_file = self._get_data_file()
        
        # 从配置中读取配置项
        try:
            if config:
                if "image_url" in config:
                    self.image_url = config["image_url"]
                    logger.info(f"从配置中读取图片模板地址：{self.image_url}")
                if "color_enabled" in config:
                    self.color_enabled = config["color_enabled"]
                    logger.info(f"从配置中读取文本多颜色状态：{self.color_enabled}")
                if "max_text_length" in config:
                    self.max_text_length = int(config["max_text_length"])
                    logger.info(f"从配置中读取文本字数上限：{self.max_text_length}")
        except Exception as e:
            logger.error(f"读取配置失败：{e}")
        
        # 设置默认值
        if not hasattr(self, 'image_mode'):
            self.image_mode = False  # 默认为关闭图片模式
        if not hasattr(self, 'image_url'):
            self.image_url = "https://api.suyanw.cn/api/comic.php"  # 默认值
        if not hasattr(self, 'color_enabled'):
            self.color_enabled = True  # 默认为开启文本多颜色
        if not hasattr(self, 'max_text_length'):
            self.max_text_length = 1000  # 默认为1000字符
        
        logger.info(f"文本转图片插件初始化，当前图片模式：{self.image_mode}，文本多颜色状态：{self.color_enabled}")
        logger.info(f"当前图片模板地址：{self.image_url}，文本字数上限：{self.max_text_length}")
    
    def _get_data_file(self):
        """获取数据文件路径"""
        # 使用插件名称作为参数获取数据目录
        data_dir = StarTools.get_data_dir("upload_text_to_image")
        import os
        return os.path.join(data_dir, "image_config.json")
    
    async def _load_data(self):
        """加载持久化数据"""
        async with self._data_lock:
            try:
                import json
                import os
                if os.path.exists(self.data_file):
                    with open(self.data_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'image_mode' in data:
                            self.image_mode = data['image_mode']
                        # 只有当 image_url 未从配置文件中设置时，才从持久化数据中加载
                        if 'image_url' in data and not hasattr(self, 'image_url'):
                            self.image_url = data['image_url']
                        # 只有当 color_enabled 未从配置文件中设置时，才从持久化数据中加载
                        if 'color_enabled' in data and not hasattr(self, 'color_enabled'):
                            self.color_enabled = data['color_enabled']
                        # 只有当 max_text_length 未从配置文件中设置时，才从持久化数据中加载
                        if 'max_text_length' in data and not hasattr(self, 'max_text_length'):
                            self.max_text_length = data['max_text_length']
                    logger.info("已从持久化数据加载配置")
            except Exception as e:
                logger.error(f"加载持久化数据失败：{e}")
    
    async def _save_data(self):
        """保存持久化数据"""
        async with self._data_lock:
            try:
                import json
                import os
                # 确保数据目录存在
                os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
                # 保存数据
                data = {
                    'image_mode': self.image_mode,
                    'image_url': self.image_url,
                    'color_enabled': self.color_enabled,
                    'max_text_length': self.max_text_length
                }
                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                logger.info("配置已持久化保存")
            except Exception as e:
                logger.error(f"保存持久化数据失败：{e}")

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
        # 加载持久化数据
        await self._load_data()
        logger.info("文本转图片插件初始化成功")

    # 注册指令的装饰器。指令名为 p。注册成功后，发送 `/p 文本` 就会触发这个指令，并将文本转换为图片返回
    @filter.command("p")
    async def text_to_image(self, event: AstrMessageEvent):
        """将文本转换为图片并发送"""
        message_str = event.message_str # 用户发的纯文本消息字符串
        logger.info(f"收到/p指令，message_str: '{message_str}'")
        
        # 提取命令参数，去除命令前缀
        if message_str is None:
            async for result in self.send_message(event, "请输入要转换为图片的文本，例如：/p 你好世界"):
                yield result
            return
        
        user_text = message_str.strip()
        # 处理两种前缀格式："/p " 和 "p "
        if user_text.startswith('/p '):
            user_text = user_text[3:].strip()
        elif user_text.startswith('p '):
            user_text = user_text[2:].strip()
        # 处理仅命令无参数的场景
        elif user_text == '/p' or user_text == 'p':
            user_text = ""
        
        logger.info(f"处理后的文本: '{user_text}'")
        
        if not user_text:
            async for result in self.send_message(event, "请输入要转换为图片的文本，例如：/p 你好世界"):
                yield result
            return
        
        # 检查文本长度，避免 URL 过长
        if len(user_text) > self.max_text_length:
            async for result in self.send_message(event, f"文本长度超过限制（{self.max_text_length}字符），请缩短文本后重试"):
                yield result
            return
        
        try:
            # 构建API请求URL
            params = {
                'image': self.image_url,
                'size': self.text_size,
                'text': user_text,
                'color': 'true' if self.color_enabled else 'false'
            }
            query_string = urllib.parse.urlencode(params)
            api_url = f"{self.api_url}?{query_string}"
            
            # 直接发送API URL作为图片
            yield event.image_result(api_url)
        except Exception as e:
            logger.error(f"生成图片时出错：{e}")
            async for result in self.send_message(event, f"生成图片时出错：{str(e)}"):
                yield result

    # 注册指令的装饰器。指令名为 tp。注册成功后，发送 `/tp` 就会触发这个指令，切换图片模式
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("tp")
    async def toggle_image_mode(self, event: AstrMessageEvent):
        """切换图片模式，开启后bot返回的内容全部使用图片形式返回"""
        self.image_mode = not self.image_mode
        status = "开启" if self.image_mode else "关闭"
        logger.info(f"图片模式已{status}，当前状态：{self.image_mode}")
        # 保存数据
        await self._save_data()
        # 发送状态消息，会根据当前图片模式决定是发送图片还是文字
        async for result in self.send_message(event, f"图片模式已{status}。\n开启后，bot返回的所有内容都会自动转换为图片形式。"):
            yield result

    # 注册指令的装饰器。指令名为 z。注册成功后，发送 `/z 图片地址` 就会触发这个指令，设置图片模板地址
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("z")
    async def set_image_url(self, event: AstrMessageEvent):
        """设置图片模板地址"""
        message_str = event.message_str # 用户发的纯文本消息字符串
        if message_str is None:
            async for result in self.send_message(event, "请输入要设置的图片模板地址，例如：/z https://example.com/image.png"):
                yield result
            return
        
        try:
            # 提取命令参数，去除命令前缀
            image_url = message_str.strip()
            # 处理两种前缀格式："/z " 和 "z "
            if image_url.startswith('/z '):
                image_url = image_url[3:].strip()
            elif image_url.startswith('z '):
                image_url = image_url[2:].strip()
            # 处理仅命令无参数的场景
            elif image_url == '/z' or image_url == 'z':
                image_url = ""
            
            # 验证 URL 合法性
            if not image_url:
                async for result in self.send_message(event, "图片模板地址不能为空"):
                    yield result
                return
            
            # 验证 URL 格式
            if not (image_url.startswith('http://') or image_url.startswith('https://')):
                async for result in self.send_message(event, "图片模板地址必须以 http:// 或 https:// 开头"):
                    yield result
                return
            
            # 更新图片模板地址
            self.image_url = image_url
            logger.info(f"图片模板地址已设置为：{self.image_url}")
            # 保存数据
            await self._save_data()
            # 发送状态消息
            async for result in self.send_message(event, f"图片模板地址已设置为：{self.image_url}"):
                yield result
        except Exception as e:
            logger.error(f"设置图片模板地址时出错：{e}")
            async for result in self.send_message(event, f"设置图片模板地址时出错：{str(e)}"):
                yield result

    # 注册指令的装饰器。指令名为 cf。注册成功后，发送 `/cf` 就会触发这个指令，切换颜色状态
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("cf")
    async def toggle_color(self, event: AstrMessageEvent):
        """切换文本多颜色状态"""
        self.color_enabled = not self.color_enabled
        status = "开启" if self.color_enabled else "关闭"
        logger.info(f"文本多颜色状态已{status}，当前状态：{self.color_enabled}")
        # 保存数据
        await self._save_data()
        # 发送状态消息
        async for result in self.send_message(event, f"文本多颜色状态已{status}。\n{status}后，生成的图片将{'包含多种颜色' if self.color_enabled else '只有一种颜色'}。"):
            yield result

    # 注册指令的装饰器。指令名为 setmax。注册成功后，发送 `/setmax 数字` 就会触发这个指令，设置文本字数上限
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("setmax")
    async def set_max_text_length(self, event: AstrMessageEvent):
        """设置文本字数上限"""
        message_str = event.message_str # 用户发的纯文本消息字符串
        if message_str is None:
            async for result in self.send_message(event, "请输入要设置的文本字数上限，例如：/setmax 2000"):
                yield result
            return
        
        try:
            # 提取命令参数，去除命令前缀
            max_length_str = message_str.strip()
            # 处理两种前缀格式："/setmax " 和 "setmax "
            if max_length_str.startswith('/setmax '):
                max_length_str = max_length_str[8:].strip()
            elif max_length_str.startswith('setmax '):
                max_length_str = max_length_str[7:].strip()
            # 处理仅命令无参数的场景
            elif max_length_str == '/setmax' or max_length_str == 'setmax':
                max_length_str = ""
            
            # 验证输入
            if not max_length_str:
                async for result in self.send_message(event, "请输入要设置的文本字数上限，例如：/setmax 2000"):
                    yield result
                return
            
            # 转换为整数
            max_length = int(max_length_str)
            
            # 验证值的合理性
            if max_length <= 0:
                async for result in self.send_message(event, "文本字数上限必须大于0"):
                    yield result
                return
            
            # 更新文本字数上限
            self.max_text_length = max_length
            logger.info(f"文本字数上限已设置为：{self.max_text_length}")
            # 保存数据
            await self._save_data()
            # 发送状态消息
            async for result in self.send_message(event, f"文本字数上限已设置为：{self.max_text_length}字符"):
                yield result
        except ValueError:
            async for result in self.send_message(event, "请输入有效的数字，例如：/setmax 2000"):
                yield result
        except Exception as e:
            logger.error(f"设置文本字数上限时出错：{e}")
            async for result in self.send_message(event, f"设置文本字数上限时出错：{str(e)}"):
                yield result



    async def send_message(self, event: AstrMessageEvent, text: str):
        """发送消息，当图片模式开启时，将文本转换为图片发送"""
        logger.info(f"发送消息：{text[:50]}...，图片模式：{self.image_mode}")
        if self.image_mode:
            try:
                # 构建API请求URL
                params = {
                    'image': self.image_url,
                    'size': self.text_size,
                    'text': text,
                    'color': 'true' if self.color_enabled else 'false'
                }
                query_string = urllib.parse.urlencode(params)
                api_url = f"{self.api_url}?{query_string}"
                logger.info(f"构建图片API URL：{api_url}")
                
                # 直接发送API URL作为图片
                yield event.image_result(api_url)
            except Exception as e:
                logger.error(f"生成图片时出错：{e}")
                # 出错时发送纯文本
                logger.info("生成图片失败，回退到纯文本")
                yield event.plain_result(text)
        else:
            # 图片模式关闭时，发送纯文本
            logger.info("图片模式关闭，发送纯文本")
            yield event.plain_result(text)

    # 发送消息前的钩子，用于将文本消息转换为图片
    @filter.on_decorating_result()
    async def on_decorating_result(self, event: AstrMessageEvent):
        """在发送消息前装饰消息，将文本转换为图片"""
        if self.image_mode:
            try:
                result = event.get_result()
                if result:
                    # 检查消息链中是否有文本消息
                    has_text = False
                    text_components = []
                    
                    for component in result.chain:
                        # 更精确的文本组件判断
                        if hasattr(component, 'text') and isinstance(component.text, str):
                            has_text = True
                            text_components.append(component.text)
                    
                    if has_text:
                        # 合并文本内容，添加分隔符
                        text_content = '\n'.join(text_components)
                        # 构建API请求URL
                        params = {
                            'image': self.image_url,
                            'size': self.text_size,
                            'text': text_content,
                            'color': 'true' if self.color_enabled else 'false'
                        }
                        query_string = urllib.parse.urlencode(params)
                        api_url = f"{self.api_url}?{query_string}"
                        
                        # 检查最终 URL 长度
                        MAX_URL_LENGTH = 2048
                        if len(api_url) > MAX_URL_LENGTH:
                            logger.warning(f"生成的图片 URL 过长：{len(api_url)} 字符，可能导致发送失败")
                            # 不转换为图片，保持原样
                            return
                        
                        logger.info(f"将文本转换为图片：{text_content[:50]}...")
                        
                        # 创建新的消息链，按原顺序重建
                        # 首先创建一个纯文本结果作为基础
                        new_result = event.plain_result("")
                        # 清空链，准备按原顺序重建
                        new_result.chain = []
                        
                        # 标记是否已添加图片
                        image_added = False
                        
                        # 遍历原始链，检查是否有文本组件
                        has_text_component = False
                        for component in result.chain:
                            if hasattr(component, 'text') and isinstance(component.text, str):
                                has_text_component = True
                                break
                        
                        # 如果有文本组件，创建图片消息
                        if has_text_component:
                            # 直接使用 event.image_result 创建图片消息
                            image_result = event.image_result(api_url)
                            # 将非文本组件添加到图片结果的 chain 中
                            for component in result.chain:
                                if not (hasattr(component, 'text') and isinstance(component.text, str)):
                                    image_result.chain.append(component)
                            # 设置新的结果
                            event.set_result(image_result)
            except Exception as e:
                logger.error(f"装饰消息时出错：{e}")

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
        logger.info("文本转图片插件已卸载")
