import type {DetectionRead,PageRead} from '../types/scanner'
import {validateDraftQuad} from './cornerGeometry.ts'

/** Shared gate for manual detection, imported proposals and initial hydration. */
export function assertDetectionProposal(result:DetectionRead,page:PageRead){
  if(result.page_id!==page.id||result.source_artifact_id!==page.normalized_artifact_id
    ||result.source_width!==page.width||result.source_height!==page.height||result.confirmed!==false
    ||!['proposed','proposed_with_warning','manual_required'].includes(result.status)
    ||(result.heuristic_score!==null&&(!Number.isFinite(result.heuristic_score)||result.heuristic_score<0||result.heuristic_score>1))
    ||(result.status==='manual_required'?result.corners!==null:!result.corners||Boolean(validateDraftQuad(result.corners,page)))){
    throw new Error('Đề xuất nhận diện không khớp trang, nguồn hoặc hình học hợp lệ.')
  }
}
