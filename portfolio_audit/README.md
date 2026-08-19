# make_gnu_ls portfolio audit

Status: **PHASE 10 candidate selected — source improvement requires a new explicit approval**

이 디렉터리는 기존 프로젝트 source와 분리된 감사 산출물이다. PHASE 0~8을 완료했으며, 고정된 GNU `ls` oracle과 25-case suite로 baseline을 측정하고 harness 검출력 및 주요 failure 원인을 검증했다. 기존 project source는 여전히 수정하지 않았다.

## Profile routing note

- USER-PROVIDED: 대상 저장소는 `make_gnu_ls`, 적용 요청은 `PROFILE B`이다.
- VERIFIED FROM PROVIDED INSTRUCTION: 첨부 문서의 `PROFILE B`는 `gnu_nm_project`용 ELF/GNU nm profile이고, `make_gnu_ls`용 profile은 `PROFILE D`이다.
- INFERENCE/APPLIED: 저장소 지정이 더 구체적이고 실제 source가 `ls` 구현이므로, CHECKPOINT A의 profile-specific 계획은 `make_gnu_ls`에 대응하는 PROFILE D(directory traversal + GNU ls comparison)로 작성했다.
- USER APPROVED: target-matched PROFILE D routing과 실제 GNU `ls` oracle 고정을 승인했다.

## Evidence labels

- `VERIFIED FROM CODE`: source에서 직접 확인
- `VERIFIED FROM RUNTIME TEST`: 실제 명령 실행으로 확인
- `USER-PROVIDED RATIONALE`: 사용자가 설명한 설계 의도
- `INFERENCE`: 코드/환경 근거에 기반한 분석
- `UNKNOWN`: 아직 증거가 부족함

## Audit files

- `baseline.md`: commit, environment, build, source integrity
- `architecture.md`: components, control flow, data/resource lifecycle, design characteristics
- `feature_inventory.md`: code-based implementation inventory and functional scope
- `test_plan.md`: proposed deterministic suite, oracle, normalization policy
- `tests/cases.json`: 25 deterministic case definitions
- `tools/run_baseline.py`: fixture generation, raw capture, semantic comparison, classification
- `tools/validate_harness.py`: five injected-defect checks
- `test_results.json`: machine-readable corrected baseline
- `test_results.md`: CHECKPOINT B matrix and important PASS evidence
- `failures.md`: five selected failure/root-cause analyses and solution architectures
- `design_rationale.md`: verified facts, author rationale, inference, and unknowns
- `improvement.md`: correctness-first candidate ranking and approval gate
- `harness_validation.json`: mutation/self-test evidence
- `raw/`: fixture manifest and unnormalized target/oracle outputs

## Integrity boundary

기존 source는 수정하지 않았다. Corrected baseline 종료 후에도 source manifest digest는 CHECKPOINT A의 digest와 동일하다. Build artifacts는 최종 검증 후 `make fclean`으로 정리했으며, 새 파일은 `portfolio_audit/` 아래에만 있다.
