# astrbot_plugin_text_to_Image
 二次元风格-文本转图片
<center>
<img src="https://count.getloli.com/@:name" alt=":tniay-astrbot-Image" width="300">
</center>

<div align="center">
  <img src="https://github.com/user-attachments/assets/4d1de02f-7347-4b2f-b81d-c2d3cfd84b87" alt="logo" width="300" />
  <p>AstrBot 插件，二次元风格文转图，使bot以图片形式返回内容，将文本以图片的形式发送。基于外部API的二次元风格文转图，提供更美观的文本展示效果。</p>
  
  <div>
    <img src="https://img.shields.io/github/stars/tniany/astrbot_plugin_text_to_Image?style=flat-square" alt="GitHub Stars" />
    <img src="https://img.shields.io/github/license/tniany/astrbot_plugin_text_to_Image?style=flat-square" alt="License" />
    <img src="https://img.shields.io/badge/python-3.7%2B-blue?style=flat-square" alt="Python Version" />
  </div>
</div>


## 功能介绍

- **单次文本转图片**：使用 `/p 文本` 指令将指定文本转换为图片并发送
- **图片模式切换**：使用 `/tp` 指令切换图片模式，开启后所有返回内容都会转换为图片
- **文本字数上限设置**：使用 `/setmax 数字` 指令（管理员权限）修改文本字数上限
- **自动错误处理**：当图片生成失败时，会自动回退到发送纯文本
- **二次元风格**：基于外部API生成的图片具有美观的二次元风格

## 效果展示

  <img src="https://github.com/user-attachments/assets/0369dd64-e7a2-494d-943a-14eb9e0e83f7" alt="效果展示" width="300" />


## 技术实现

- 使用 `aiohttp` 库进行异步HTTP请求
- 调用外部API生成图片
- 支持文本URL编码和完整的错误处理机制
- 兼容多种聊天平台

## 安装方法

### 方法一：插件市场安装（推荐）
在 AstrBot 插件市场中搜索 **二次元风格-文本转图片**，点击下载安装即可。

### 方法二：手动安装
1. 克隆或下载本插件到 AstrBot 的插件目录
   ```bash
   git clone https://github.com/tniany/astrbot_plugin_text_to_Image.git
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 重启 AstrBot 即可使用

## 使用示例

### 单次文本转图片

```
/p 你好，这是一条测试消息
```

### 切换图片模式

```
/tp
# 回复：图片模式已开启

/tp
# 回复：图片模式已关闭
```

### 设置文本字数上限

```
/setmax 2000
# 回复：文本字数上限已设置为：2000字符

/setmax 500
# 回复：文本字数上限已设置为：500字符

#url过长api可能无法正常返回内容
```

## 依赖

- Python 3.7+
- aiohttp

## 许可证

[MIT](LICENSE)

## 作者

浅月tniay

## 版本

v1.1.1

## 更新日志

### v1.1.1
- 完善插件配置页面并修复已知bug
  
-图片模板地址
用于生成图片的模板地址，默认使用二次元风格模板

-开启/关闭 文本多颜色
开启后生成的图片将包含多种颜色，关闭后生成的图片将只有一种颜色

-文本字数上限
生成图片时的文本字数上限，超过此限制将拒绝生成图片

-URL长度上限
生成的图片URL长度上限，超过此限制将不转换为图片
```
url过长api可能无法正常返回内容
```
### v1.1.0
- 添加文本字数上限配置项 `max_text_length`
- 新增 `/setmax` 指令（管理员权限），用于修改文本字数上限
- 添加URL长度上限配置项 `max_url_length`
- 文本字数上限默认值为 1000 字符
- URL长度上限默认值为 2048 字符
- 将硬编码的文本长度限制改为可配置的动态值
- 将硬编码的URL长度限制改为可配置的动态值
- 优化了配置读取和持久化逻辑

### v1.0.6
- 优化错误处理机制
- 提升图片生成成功率

### v1.0.5
- 修复部分平台兼容性问题
- 优化API调用逻辑

### v1.0.0
- 初始版本发布
- 实现基本的文本转图片功能
- 支持图片模式切换


## 仓库地址

[GitHub](https://github.com/tniany/astrbot_plugin_text_to_Image)
