# S3E Calibration Tools

## 中文简介

这是一个用于处理 S3E 数据集标定参数的小工具仓库，当前主要用于：

- 读取 OpenCV YAML 标定文件（如 `alpha.yaml`、`bob.yaml`、`carol.yaml`）
- 计算并转换相机、IMU、LiDAR 之间的外参矩阵
- 导出统一格式的外参文件（如 `*_extrinsics.yaml`）

## English Overview

This repository provides simple tools for processing calibration parameters in the S3E dataset.  
Current features include:

- Reading OpenCV-style YAML calibration files (e.g., `alpha.yaml`, `bob.yaml`, `carol.yaml`)
- Computing and converting extrinsic transforms among Camera, IMU, and LiDAR
- Exporting standardized extrinsic files (e.g., `*_extrinsics.yaml`)

## Quick Start

```bash
uv venv .venv --python 3
uv pip install --python .venv/bin/python numpy pyyaml
```

```bash
.venv/bin/python extrinsic_compute.py --yaml alpha.yaml
```

Optional output path:

```bash
.venv/bin/python extrinsic_compute.py --yaml alpha.yaml --out alpha_extrinsics.yaml
```

## Dataset Source / 数据集来源

S3E dataset (Hugging Face):  
https://huggingface.co/datasets/PengYu-Team/S3E/tree/main/S3Ev1

