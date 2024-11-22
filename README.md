# VPN-Subscription-Cache

一个用于缓存 VPN 订阅的工具，相当于一个带缓存的反向代理。

适用场景：

- 机场限制了每日订阅次数以限制共享账号，但是你又想和多个朋友共用。
- 机场订阅地址经常变动，手动更新每个设备太麻烦。
- 机场订阅地址网络不稳定，设备经常无法访问。

功能特性：

- 支持基于朴素字符串 token 的简单鉴权。
- 透传下游并统一用户 UA 以支持自适应不同客户端、减少回源次数。
- 透传上游响应头以支持特殊功能。（例如 Subscription-Userinfo 头）

部署方法：

1. `git clone https://github.com/ChrisKimZHT/VPN-Subscription-Cache`
2. `cd VPN-Subscription-Cache`
3. `docker build -t vpn-subscription-cache .`
4. `docker run -d -p 9000:9000 -e SUBSCRIBE_URL=xxx vpn-subscription-cache`

环境变量：

- `SUBSCRIBE_URL`：订阅地址，**必填**。
- `USER_TOKEN`：用户鉴权 token，选填，空则不鉴权。
- `ADMIN_TOKEN`：管理员鉴权 token，选填，空则禁用。
- `CACHE_TIMEOUT`：缓存超时时间/秒，选填，默认一天。

使用方法：

- 访问 `http://your-host:9000/subscribe` 即可获取订阅内容。
- 访问 `http://your-host:9000/purge` 可以清除所有缓存（管理功能）。
- 访问 `http://your-host:9000/list` 可以列出所有缓存（管理功能）。
- 如有鉴权，请在链接尾部加上 `?token=yourtoken`。