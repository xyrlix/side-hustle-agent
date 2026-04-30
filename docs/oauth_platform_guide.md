# 各平台 OAuth 权限申请指南

本文档详细说明副业雷达系统支持的内容平台 OAuth 权限申请流程。

---

## 目录

- [微信公众号](#1-微信公众号-wechat-public-platform)
- [头条号](#2-头条号-toutiao)
- [小红书](#3-小红书-xiaohongshu)
- [知乎](#4-知乎-zhihu)
- [项目配置](#项目配置)
- [常见问题](#常见问题)

---

## 1. 微信公众号 (WeChat Public Platform)

### 申请入口

https://mp.weixin.qq.com

### 申请流程

#### 1.1 注册公众号

1. 访问微信公众平台官网，点击"立即注册"
2. 选择账号类型：
   - **订阅号**：个人可注册，每天可群发 1 次
   - **服务号**：企业/组织可注册，每月可群发 4 次，支持更多高级接口
   - **企业号**：企业内部使用
3. 填写邮箱、密码等基本信息
4. 完成主体类型选择（个人/企业/政府/其他组织）
5. 上传主体资质文件，完成认证

#### 1.2 获取 AppID 和 AppSecret

1. 登录微信公众平台
2. 进入 **设置与开发** → **基本配置**
3. 获取 `AppID`（开发者 ID）
4. 点击"生成"按钮获取 `AppSecret`（开发者密码），请妥善保存

#### 1.3 配置授权回调域名

1. 进入 **设置与开发** → **公众号设置** → **功能设置**
2. 找到 **网页授权域名**，点击"设置"
3. 下载验证文件（`.txt` 文件）
4. 将验证文件上传到服务器根目录（确保可通过 `http://your-domain.com/MP_verify_xxx.txt` 访问）
5. 填写回调域名（如：`your-domain.com`）

#### 1.4 第三方平台授权（如适用）

如果是第三方平台开发模式：

1. 在微信公众平台创建第三方平台账号
2. 获取 `component_appid` 和 `component_secret`
3. 配置授权事件接收 URL
4. 配置消息校验 Token 和 EncodingAESKey

### 所需权限说明

| 权限 | 说明 | 获取方式 |
|------|------|----------|
| `snsapi_base` | 静默授权，仅获取 openid | 默认开通 |
| `snsapi_userinfo` | 获取用户基本信息 | 需在授权 URL 中指定 |
| 群发消息 | 向粉丝推送消息 | 服务号认证后 |
| 自定义菜单 | 设置公众号菜单 | 默认开通 |
| 素材管理 | 上传/获取素材 | 默认开通 |

### 注意事项

- 个人订阅号无法进行微信认证，部分高级接口不可用
- 服务号认证需支付 300 元/年认证费
- 网页授权域名必须完成 ICP 备案

---

## 2. 头条号 (Toutiao)

### 申请入口

- 头条号平台：https://mp.toutiao.com
- 头条开放平台：https://open.douyin.com（字节跳动统一开放平台）

### 申请流程

#### 2.1 注册头条号

1. 访问头条号平台 https://mp.toutiao.com
2. 使用手机号注册
3. 选择账号类型（个人/企业/媒体）
4. 完成实名认证（需上传身份证）
5. 填写账号信息（名称、头像、简介）

#### 2.2 申请 API 权限

头条号 API 权限申请方式：

**方式一：通过字节跳动开放平台**

1. 访问 https://open.douyin.com
2. 注册开发者账号
3. 创建应用，填写应用信息：
   - 应用名称
   - 应用描述
   - 应用官网
   - 应用场景说明
4. 选择需要的权限（如：内容发布、数据查询等）
5. 提交审核

**方式二：商务合作**

1. 联系头条开放平台商务团队
2. 提交合作方案和需求说明
3. 签订合作协议
4. 获取 API 访问权限

#### 2.3 获取凭证

1. 应用审核通过后，进入应用管理页面
2. 获取 `Client Key`（即 client_id）
3. 获取 `Client Secret`（即 client_secret）

#### 2.4 配置回调地址

1. 在应用设置中找到"授权回调地址"
2. 添加你的回调 URL（如：`http://your-domain.com/callback/toutiao`）
3. 保存配置

### 权限说明

| 权限 | 说明 | 获取方式 |
|------|------|----------|
| 内容发布 | 发布文章、视频 | 需申请 |
| 内容管理 | 查询、删除内容 | 需申请 |
| 用户信息 | 获取授权用户信息 | 默认 |
| 数据分析 | 获取内容阅读、互动数据 | 需申请 |

### 注意事项

- 头条号 API 权限审核较为严格，个人开发者较难获得
- 建议通过第三方服务商或 MCN 机构获取权限
- 回调域名需完成 ICP 备案

---

## 3. 小红书 (Xiaohongshu)

### 申请入口

https://open.xiaohongshu.com

### 申请流程

#### 3.1 注册开放平台账号

1. 访问小红书开放平台 https://open.xiaohongshu.com
2. 使用手机号注册
3. 完成开发者认证：
   - 个人开发者：上传身份证
   - 企业开发者：上传营业执照

#### 3.2 创建应用

1. 登录开放平台控制台
2. 点击"创建应用"
3. 填写应用信息：
   - **应用名称**：清晰描述应用功能
   - **应用描述**：详细说明应用场景和用途
   - **应用官网**：你的网站地址
   - **应用图标**：符合规范的图标
4. 选择应用类型（网站应用/移动应用）

#### 3.3 申请权限

1. 在应用管理页面，进入"权限管理"
2. 选择需要的权限：
   - 用户信息授权
   - 笔记发布权限
   - 笔记查询权限
   - 图片上传权限
3. 提交权限申请，说明使用场景

#### 3.4 获取凭证

1. 应用审核通过后
2. 进入应用基本信息页面
3. 获取 `Client ID`（App Key）
4. 获取 `Client Secret`（App Secret）

#### 3.5 配置回调地址

1. 进入应用设置 → 开发设置
2. 添加授权回调 URL
3. 示例：`http://your-domain.com/callback/xiaohongshu`
4. 保存配置

### 权限说明

| 权限 | 说明 | 获取方式 |
|------|------|----------|
| 用户信息 | 获取用户昵称、头像 | 默认 |
| 笔记发布 | 代用户发布笔记 | 需申请 |
| 笔记管理 | 查询、删除笔记 | 需申请 |
| 图片上传 | 上传图片到平台 | 需申请 |

### 注意事项

- 小红书 API 审核严格，需详细说明使用场景
- 笔记发布权限可能需要额外审核
- 内容有审核机制，违规内容会被下架
- 回调域名建议完成 ICP 备案
- 遵守小红书社区规范和内容标准

---

## 4. 知乎 (Zhihu)

### 申请入口

https://www.zhihu.com/developers

### 申请流程

#### 4.1 注册开发者账号

1. 访问知乎开放平台
2. 使用知乎账号登录
3. 申请成为开发者

#### 4.2 创建应用

1. 进入开发者控制台
2. 点击"创建应用"
3. 填写应用信息：
   - 应用名称
   - 应用描述
   - 回调地址
   - 应用图标

#### 4.3 获取凭证

1. 应用创建成功后
2. 获取 `App Key`（即 client_id）
3. 获取 `App Secret`（即 client_secret）

### 权限说明

| 权限 | 说明 | 获取方式 |
|------|------|----------|
| 用户信息 | 获取用户基本信息 | 默认 |
| 内容查询 | 查询问题、回答、文章 | 默认 |
| 内容发布 | 发布回答、文章 | 需申请 |

### 注意事项

- 知乎开放 API 相对有限
- 部分内容发布权限可能需要特殊申请
- 调用频率有限制，注意遵守 API 调用规范

---

## 项目配置

### 环境变量配置

在项目根目录创建 `.env` 文件（或复制 `.env.example` 并修改），配置各平台的 OAuth 凭证：

```bash
# ==================== 微信公众号 ====================
WECHAT_APPID=your_wechat_appid
WECHAT_APP_SECRET=your_wechat_app_secret
WECHAT_REDIRECT_URI=http://your-domain.com/callback/wechat

# ==================== 头条号 ====================
TOUTIAO_CLIENT_ID=your_toutiao_client_id
TOUTIAO_CLIENT_SECRET=your_toutiao_client_secret
TOUTIAO_REDIRECT_URI=http://your-domain.com/callback/toutiao

# ==================== 小红书 ====================
XHS_CLIENT_ID=your_xhs_client_id
XHS_CLIENT_SECRET=your_xhs_client_secret
XHS_REDIRECT_URI=http://your-domain.com/callback/xiaohongshu

# ==================== 知乎 ====================
ZHIHU_APP_KEY=your_zhihu_app_key
ZHIHU_APP_SECRET=your_zhihu_app_secret
ZHIHU_REDIRECT_URI=http://your-domain.com/callback/zhihu
```

### 代码中使用

```python
from side_hustle_agent.platforms import get_platform

# 获取平台实例
platform = get_platform("wechat_public")

# 生成授权链接
auth_url = platform.get_authorization_url()
print(f"请访问以下链接进行授权: {auth_url}")

# 用户授权后，用授权码换取 token
result = platform.exchange_code_for_token(code="authorization_code_here")

# 使用 token 调用 API
user_info = platform.get_user_info()
```

---

## 常见问题

### Q1: 回调域名必须备案吗？

**A:** 大多数国内平台（微信、头条、小红书）要求回调域名完成 ICP 备案。建议使用已备案的域名。

### Q2: 个人开发者能申请到所有权限吗？

**A:** 不能。部分平台（如头条号、小红书）的高级 API 权限主要面向企业开发者。个人开发者可以考虑：
- 通过 MCN 机构合作
- 使用第三方服务商
- 申请成为企业认证开发者

### Q3: 审核周期多久？

**A:** 
- 微信公众号：1-7 个工作日
- 头条号：3-7 个工作日
- 小红书：5-10 个工作日
- 知乎：3-5 个工作日

### Q4: 回调地址配置错误怎么办？

**A:** 可以在各平台的开发者控制台重新配置回调地址，修改后即时生效。

### Q5: Token 过期如何处理？

**A:** 各平台提供 refresh_token 机制，在 access_token 过期前使用 refresh_token 刷新获取新的 token。项目中已实现 `refresh_access_token()` 方法。

### Q6: 如何测试 OAuth 流程？

**A:** 
1. 使用各平台提供的沙箱环境（如有）
2. 使用本地开发环境，配置 hosts 指向 localhost
3. 使用 ngrok 等内网穿透工具提供公网访问

---

## 相关链接

- [微信公众平台开发者文档](https://developers.weixin.qq.com/doc/)
- [字节跳动开放平台](https://open.douyin.com/)
- [小红书开放平台](https://open.xiaohongshu.com/)
- [知乎开放平台](https://www.zhihu.com/developers)

---

> 最后更新：2026-04-30
> 如有问题，请提交 Issue 或联系开发团队
