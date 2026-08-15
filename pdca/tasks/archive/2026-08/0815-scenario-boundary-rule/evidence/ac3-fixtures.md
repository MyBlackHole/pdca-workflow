# ac3-fixtures.md

{
  "task_id": "T0273",
  "check": "AC-3",
  "assertion": "历史错配任务 T0268-T0272 判定为 development",
  "runs": [
    {
      "tid": "T0268",
      "desc": "brief-effectiveness-audit",
      "code": true,
      "expect": "development"
    },
    {
      "tid": "T0269",
      "desc": "brief-recall-loop",
      "code": true,
      "expect": "development"
    },
    {
      "tid": "T0270",
      "desc": "gate-compliance-audit",
      "code": true,
      "expect": "development"
    },
    {
      "tid": "T0271",
      "desc": "gate-compliance-remediation",
      "code": true,
      "expect": "development"
    },
    {
      "tid": "T0272",
      "desc": "self-audit",
      "code": true,
      "expect": "development"
    },
    {
      "tid": "T0163",
      "desc": "pg/mysql parquet poc（额外发现）",
      "code": true,
      "expect": "development"
    }
  ],
  "result": "PASSED"
}
