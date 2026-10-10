def verify_package_layout(package_dir: str) -> tuple:
    """对照契约清单逐项检查包内文件存在性与入口可导入性，返回 (通过, 差异清单)。"""
    raise NotImplementedError("unimplemented:fn:verify_package_layout")
