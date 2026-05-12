#!/usr/bin/env python3
import argparse
from pathlib import Path

import numpy as np
import yaml


def _opencv_matrix_constructor(loader: yaml.Loader, node: yaml.Node) -> np.ndarray:
    value = loader.construct_mapping(node, deep=True)
    rows = int(value["rows"])
    cols = int(value["cols"])
    data = value["data"]
    return np.array(data, dtype=float).reshape(rows, cols)


class OpenCvYamlLoader(yaml.SafeLoader):
    pass


OpenCvYamlLoader.add_constructor("tag:yaml.org,2002:opencv-matrix", _opencv_matrix_constructor)


def load_config(yaml_path: Path) -> dict:
    text = yaml_path.read_text(encoding="utf-8")
    # OpenCV YAML often starts with `%YAML:1.0`, which is not standard YAML.
    if text.startswith("%YAML:1.0"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
    return yaml.load(text, Loader=OpenCvYamlLoader)


def get_matrix(cfg: dict, key: str) -> np.ndarray:
    if key not in cfg:
        raise KeyError(f"YAML missing key: {key}")
    mat = np.array(cfg[key], dtype=float)
    if mat.shape != (4, 4):
        raise ValueError(f"{key} must be 4x4, got {mat.shape}")
    return mat


def fmt(name: str, mat: np.ndarray, precision: int) -> str:
    arr = np.array2string(
        mat,
        formatter={"float_kind": lambda x: f"{x:.{precision}f}"},
    )
    return f"{name} =\n{arr}\n"


def _opencv_matrix_block(name: str, mat: np.ndarray, precision: int) -> str:
    row_texts = []
    for row in mat:
        row_text = ", ".join(f"{float(x):.{precision}f}" for x in row)
        row_texts.append(row_text)

    if len(row_texts) == 1:
        data_block = f"  data: [{row_texts[0]}]"
    else:
        data_lines = [f"  data: [{row_texts[0]},"]
        for row_text in row_texts[1:-1]:
            data_lines.append(f"         {row_text},")
        data_lines.append(f"         {row_texts[-1]}]")
        data_block = "\n".join(data_lines)

    return (
        f"{name}: !!opencv-matrix\n"
        "  rows: 4\n"
        "  cols: 4\n"
        "  dt: d\n"
        f"{data_block}\n"
    )


def save_extrinsics(output_path: Path, matrices: dict[str, np.ndarray], precision: int) -> None:
    parts = ["%YAML:1.0", "---"]
    for key, value in matrices.items():
        parts.append(_opencv_matrix_block(key, value, precision).rstrip())
    content = "\n\n".join(parts) + "\n"
    output_path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute extrinsic transforms from OpenCV-style YAML.")
    parser.add_argument("--yaml", default="alpha.yaml", help="Path to calibration yaml.")
    parser.add_argument("--precision", type=int, default=6, help="Print precision.")
    parser.add_argument("--out", default=None, help="Output extrinsic yaml path.")
    args = parser.parse_args()

    input_path = Path(args.yaml)
    output_path = Path(args.out) if args.out else input_path.with_name(f"{input_path.stem}_extrinsics.yaml")

    cfg = load_config(input_path)
    t_i_c = get_matrix(cfg, "Tic")  # left camera -> imu
    t_l_c = get_matrix(cfg, "Tlc")  # left camera -> lidar

    t_c_i = np.linalg.inv(t_i_c)
    t_c_l = np.linalg.inv(t_l_c)
    t_l_i = t_l_c @ t_c_i
    t_i_l = np.linalg.inv(t_l_i)

    print(fmt("T_i_c (camera -> imu)", t_i_c, args.precision))
    print(fmt("T_l_c (camera -> lidar)", t_l_c, args.precision))
    print(fmt("T_c_i (imu -> camera)", t_c_i, args.precision))
    print(fmt("T_c_l (lidar -> camera)", t_c_l, args.precision))
    print(fmt("T_l_i (imu -> lidar)", t_l_i, args.precision))
    print(fmt("T_i_l (lidar -> imu)", t_i_l, args.precision))

    output_matrices = {
        "T_i_c": t_i_c,
        "T_l_c": t_l_c,
        "T_c_i": t_c_i,
        "T_c_l": t_c_l,
        "T_l_i": t_l_i,
        "T_i_l": t_i_l,
    }
    save_extrinsics(output_path, output_matrices, args.precision)
    print(f"Saved extrinsics to: {output_path}")


if __name__ == "__main__":
    main()
