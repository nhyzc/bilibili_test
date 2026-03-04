# bilibili_test

一个可直接运行的 B 站视频封面爬取小项目：
- 支持通过 `视频 URL` / `BV 号` / `av 号(aid)` 获取封面链接。
- 支持将封面图片下载到本地。

## 1. 安装依赖

```bash
python -m pip install -r requirements.txt
```

## 2. 获取封面链接

### 方式 A：传视频链接

```bash
python bilibili_cover_fetcher.py --url "https://www.bilibili.com/video/BV1xx411c7mD"
```

### 方式 B：传 BV 号

```bash
python bilibili_cover_fetcher.py --bvid "BV1xx411c7mD"
```

### 方式 C：传 av 号（aid）

```bash
python bilibili_cover_fetcher.py --aid 170001
```

## 3. 下载封面到本地

```bash
python bilibili_cover_fetcher.py \
  --url "https://www.bilibili.com/video/BV1xx411c7mD" \
  --download "./output/cover.jpg"
```

## 4. 运行测试

```bash
pytest -q
```

## 说明

项目通过 B 站公开接口：
`https://api.bilibili.com/x/web-interface/view`

获取返回 JSON 中的 `data.pic` 字段作为封面地址。
