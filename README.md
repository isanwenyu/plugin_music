##  音乐插件
这个项目是[chatgpt-on-wechat](https://github.com/zhayujie/chatgpt-on-wechat) 的音乐插件, 实现以下功能：
- [x] 使用chatgpt 推荐音乐并发送播放链
- [x] 点歌

### 使用方式
#### 插件集成
1. 把项目解压到chatgpt-on-wechat/plugins/plugin_music/ 目录下
2. 配置 chatgpt-on-wechat/plugins/plugins.json
 ```json
{
  "Music": {
    "enabled": true,
    "priority": 0
  }
}
```
3. 安装插件的依赖
```shell
cd /chatgpt-on-wechat/plugins/plugin_music/
pip3 install -r requirements.txt
```
4. 配置网易云邮箱和md5后的密码 /chatgpt-on-wechat/plugins/plugin_music/config.json
```shell
cp config.json.example config.json

{
  "username": "",
  "passwd_md5":""
}

```
5. 重新启动chatgpt-on-wechat
#### 触发
<关键字><空格><指令>:<内容>
- 点歌: `$music 点歌 可惜我是水瓶座-杨千嬅`
- 推荐: `$music 推荐一首粤语歌曲`

#### 效果

![img.png](img.png)



