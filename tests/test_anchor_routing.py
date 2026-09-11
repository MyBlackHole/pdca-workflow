"""T2152 默认锚定收紧：领域关键词路由单测。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import unittest

from task_identity import _route_anchor_by_domain


class AnchorRoutingTest(unittest.TestCase):
    def test_bcachefs(self):
        self.assertEqual(
            _route_anchor_by_domain("bcachefs 深潜", "0906-bcachefs-deep"),
            "ontology:concept/domain-bcachefs",
        )

    def test_core_prefix_routes_bcachefs_family(self):
        self.assertEqual(
            _route_anchor_by_domain("core 分配器", "core-alloc-wfq"),
            "ontology:concept/domain-core",
        )

    def test_zfs(self):
        self.assertEqual(
            _route_anchor_by_domain("ZFS ARC", "0903-zfs-arc"),
            "ontology:concept/domain-zfs",
        )

    def test_report_center(self):
        self.assertEqual(
            _route_anchor_by_domain("报表中心采集", "0907-report-center-x"),
            "ontology:concept/domain-report-center",
        )

    def test_plain_pdca_falls_back(self):
        self.assertIsNone(_route_anchor_by_domain("PDCA本体落地", "0910-pdca-landing-a"))
        self.assertIsNone(_route_anchor_by_domain("修复门禁", "0910-gatefix"))

    def test_report_alone_does_not_route(self):
        # 'report' 通用词不触发，仅 'report-center' 精确命中
        self.assertIsNone(_route_anchor_by_domain("研究报告", "0910-research-report"))


if __name__ == "__main__":
    unittest.main()
