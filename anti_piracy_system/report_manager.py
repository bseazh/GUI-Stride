"""举报流程管理模块

负责记录举报历史、管理举报证据、生成举报报告
"""

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Optional
import base64


@dataclass
class ReportRecord:
    """举报记录"""

    report_id: str  # 举报ID
    platform: str  # 平台名称(小红书/闲鱼等)
    target_title: str  # 目标商品标题
    target_shop: str  # 目标店铺名称
    target_price: float  # 目标价格
    target_url: Optional[str] = None  # 目标链接
    detection_result: Optional[Dict] = None  # 检测结果
    report_reason: str = ""  # 举报理由
    report_status: str = "pending"  # 举报状态: pending/submitted/success/failed
    evidence_screenshots: List[str] = None  # 证据截图路径列表
    reported_at: str = None  # 举报时间
    notes: Optional[str] = None  # 备注

    def __post_init__(self):
        if self.reported_at is None:
            self.reported_at = datetime.now().isoformat()
        if self.evidence_screenshots is None:
            self.evidence_screenshots = []

    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'ReportRecord':
        """从字典创建对象"""
        return cls(**data)


class ReportManager:
    """举报管理器"""

    def __init__(self, log_path: str = "logs/report_history.json"):
        """
        初始化举报管理器

        Args:
            log_path: 举报记录文件路径
        """
        self.log_path = log_path
        self.reports: Dict[str, ReportRecord] = {}
        self._ensure_log_exists()
        self.load()

    def _ensure_log_exists(self):
        """确保日志文件和目录存在"""
        log_dir = os.path.dirname(self.log_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        if not os.path.exists(self.log_path):
            with open(self.log_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

    def load(self) -> None:
        """加载举报记录"""
        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.reports = {
                    rid: ReportRecord.from_dict(rdata)
                    for rid, rdata in data.items()
                }
            print(f"✅ 已加载 {len(self.reports)} 条举报记录")
        except Exception as e:
            print(f"⚠️ 加载举报记录失败: {e}")
            self.reports = {}

    def save(self) -> None:
        """保存举报记录"""
        try:
            data = {rid: r.to_dict() for rid, r in self.reports.items()}
            with open(self.log_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ 已保存 {len(self.reports)} 条举报记录")
        except Exception as e:
            print(f"❌ 保存举报记录失败: {e}")

    def create_report(
        self,
        platform: str,
        target_title: str,
        target_shop: str,
        target_price: float,
        detection_result: Optional[Dict] = None,
        target_url: Optional[str] = None
    ) -> ReportRecord:
        """
        创建新的举报记录

        Args:
            platform: 平台名称
            target_title: 目标商品标题
            target_shop: 目标店铺名称
            target_price: 目标价格
            detection_result: 检测结果
            target_url: 目标链接

        Returns:
            举报记录对象
        """
        # 生成举报ID
        report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.reports)}"

        # 生成举报理由
        report_reason = self._generate_report_reason(detection_result)

        # 创建举报记录
        report = ReportRecord(
            report_id=report_id,
            platform=platform,
            target_title=target_title,
            target_shop=target_shop,
            target_price=target_price,
            target_url=target_url,
            detection_result=detection_result,
            report_reason=report_reason,
            report_status="pending"
        )

        self.reports[report_id] = report
        self.save()

        print(f"✅ 创建举报记录: {report_id}")
        return report

    def _generate_report_reason(self, detection_result: Optional[Dict]) -> str:
        """
        生成举报理由

        Args:
            detection_result: 检测结果

        Returns:
            举报理由文本
        """
        if not detection_result:
            return "疑似盗版内容"

        reasons = detection_result.get('reasons', [])
        confidence = detection_result.get('confidence', 0.0)

        reason_text = f"根据系统检测(置信度{confidence:.0%}),该商品疑似盗版,具体依据如下:\n"
        for i, reason in enumerate(reasons, 1):
            reason_text += f"{i}. {reason}\n"

        # 添加匹配的正版商品信息
        if detection_result.get('matched_product_name'):
            reason_text += f"\n该商品疑似盗版自正版商品: {detection_result['matched_product_name']}"

        return reason_text

    def add_screenshot(self, report_id: str, screenshot_path: str) -> bool:
        """
        添加证据截图

        Args:
            report_id: 举报ID
            screenshot_path: 截图文件路径

        Returns:
            是否添加成功
        """
        if report_id not in self.reports:
            print(f"❌ 举报记录不存在: {report_id}")
            return False

        report = self.reports[report_id]
        if screenshot_path not in report.evidence_screenshots:
            report.evidence_screenshots.append(screenshot_path)
            self.save()
            print(f"✅ 已添加截图: {screenshot_path}")
            return True

        return False

    def update_status(
        self,
        report_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> bool:
        """
        更新举报状态

        Args:
            report_id: 举报ID
            status: 新状态(pending/submitted/success/failed)
            notes: 备注信息

        Returns:
            是否更新成功
        """
        if report_id not in self.reports:
            print(f"❌ 举报记录不存在: {report_id}")
            return False

        report = self.reports[report_id]
        report.report_status = status
        if notes:
            report.notes = notes

        self.save()
        print(f"✅ 已更新举报状态: {report_id} -> {status}")
        return True

    def get_report(self, report_id: str) -> Optional[ReportRecord]:
        """
        获取举报记录

        Args:
            report_id: 举报ID

        Returns:
            举报记录对象或None
        """
        return self.reports.get(report_id)

    def get_reports_by_platform(self, platform: str) -> List[ReportRecord]:
        """
        根据平台获取举报记录

        Args:
            platform: 平台名称

        Returns:
            举报记录列表
        """
        return [r for r in self.reports.values() if r.platform == platform]

    def get_reports_by_status(self, status: str) -> List[ReportRecord]:
        """
        根据状态获取举报记录

        Args:
            status: 举报状态

        Returns:
            举报记录列表
        """
        return [r for r in self.reports.values() if r.report_status == status]

    def get_statistics(self) -> Dict:
        """
        获取统计信息

        Returns:
            统计信息字典
        """
        total = len(self.reports)
        by_platform = {}
        by_status = {}

        for report in self.reports.values():
            # 统计平台分布
            by_platform[report.platform] = by_platform.get(report.platform, 0) + 1

            # 统计状态分布
            by_status[report.report_status] = by_status.get(report.report_status, 0) + 1

        return {
            "total_reports": total,
            "by_platform": by_platform,
            "by_status": by_status
        }

    def generate_report_summary(self, report_id: str) -> str:
        """
        生成举报摘要

        Args:
            report_id: 举报ID

        Returns:
            举报摘要文本
        """
        report = self.get_report(report_id)
        if not report:
            return "举报记录不存在"

        summary = f"""
=== 举报摘要 ===
举报ID: {report.report_id}
平台: {report.platform}
商品标题: {report.target_title}
店铺名称: {report.target_shop}
商品价格: ¥{report.target_price}
举报状态: {report.report_status}
举报时间: {report.reported_at}

举报理由:
{report.report_reason}

证据截图数量: {len(report.evidence_screenshots)}
"""
        if report.notes:
            summary += f"\n备注: {report.notes}"

        return summary

    def export_to_file(self, output_path: str, format: str = "json") -> bool:
        """
        导出举报记录到文件

        Args:
            output_path: 输出文件路径
            format: 导出格式(json/txt)

        Returns:
            是否导出成功
        """
        try:
            if format == "json":
                with open(output_path, 'w', encoding='utf-8') as f:
                    data = {rid: r.to_dict() for rid, r in self.reports.items()}
                    json.dump(data, f, ensure_ascii=False, indent=2)
            elif format == "txt":
                with open(output_path, 'w', encoding='utf-8') as f:
                    for report in self.reports.values():
                        f.write(self.generate_report_summary(report.report_id))
                        f.write("\n" + "=" * 50 + "\n\n")
            else:
                print(f"❌ 不支持的导出格式: {format}")
                return False

            print(f"✅ 已导出举报记录到: {output_path}")
            return True
        except Exception as e:
            print(f"❌ 导出失败: {e}")
            return False


# 示例使用
if __name__ == "__main__":
    # 创建举报管理器
    manager = ReportManager("../logs/report_history.json")

    # 创建测试举报记录
    detection_result = {
        "is_piracy": True,
        "confidence": 0.85,
        "reasons": [
            "❌ 店铺名称'某个人卖家'不在官方授权列表中",
            "❌ 价格异常: ¥9.9 仅为原价¥199.0的5%",
            "✅ 内容匹配度高: 90%"
        ],
        "matched_product_name": "薛兆丰的经济学课"
    }

    report = manager.create_report(
        platform="小红书",
        target_title="薛兆丰经济学课程 超低价",
        target_shop="某个人卖家",
        target_price=9.9,
        detection_result=detection_result
    )

    print("\n=== 举报摘要 ===")
    print(manager.generate_report_summary(report.report_id))

    # 添加截图
    manager.add_screenshot(report.report_id, "screenshots/evidence_001.png")

    # 更新状态
    manager.update_status(report.report_id, "submitted", "已通过小红书举报功能提交")

    # 统计信息
    print("\n=== 统计信息 ===")
    stats = manager.get_statistics()
    print(f"总举报数: {stats['total_reports']}")
    print(f"平台分布: {stats['by_platform']}")
    print(f"状态分布: {stats['by_status']}")
