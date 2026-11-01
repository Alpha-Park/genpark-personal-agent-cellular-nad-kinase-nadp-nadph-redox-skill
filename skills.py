# -*- coding: utf-8 -*-
"""GenPark Industrial Skill: genpark-personal-agent-cellular-nad-kinase-nadp-nadph-redox-skill
Category: personal_agent
Website: https://www.genpark.ai
LinkedIn: https://www.linkedin.com/company/92955550
"""
import sys
import json
import math

sys.stdout.reconfigure(encoding="utf-8")

def assess_nadk_nadph_redox_flux(nadk_activity_u_mg, nadph_umol_l, nadp_plus_umol_l, reduced_gsh_to_gssg_ratio=35.0):
    if nadph_umol_l <= 0 or nadp_plus_umol_l <= 0:
        raise ValueError("NADPH and NADP+ concentrations must be positive numbers")
        
    nadph_ratio = nadph_umol_l / nadp_plus_umol_l
    
    # Healthy mitochondrial/cytosolic NADPH/NADP+ ratio is typically > 3.0 to maintain GSH in reduced state
    # GSH/GSSG ratio normal > 30.0; severe oxidative stress < 10.0
    if nadph_ratio >= 3.5 and reduced_gsh_to_gssg_ratio >= 30.0:
        status = "ROBUST_REDUCTIVE_BUFFER"
        ferroptosis_shield = "STRONG"
    elif nadph_ratio >= 2.0:
        status = "COMPROMISED_ANTIOXIDANT_RESERVE"
        ferroptosis_shield = "MODERATE"
    else:
        status = "SEVERE_REDOX_COLLAPSE"
        ferroptosis_shield = "VULNERABLE_OXIDATIVE_CELL_DEATH"
        
    reductive_capacity_score = min(100.0, (nadph_ratio / 4.0) * 50.0 + (reduced_gsh_to_gssg_ratio / 40.0) * 50.0)
    
    return {
        "nadk_specific_activity_u_mg": round(nadk_activity_u_mg, 2),
        "nadph_umol_l": round(nadph_umol_l, 2),
        "nadp_plus_umol_l": round(nadp_plus_umol_l, 2),
        "nadph_to_nadp_ratio": round(nadph_ratio, 2),
        "reduced_gsh_to_gssg_ratio": round(reduced_gsh_to_gssg_ratio, 1),
        "cellular_reductive_capacity_score": round(reductive_capacity_score, 1),
        "redox_buffer_status": status,
        "ferroptosis_protection_tier": ferroptosis_shield,
        "guidance": "Enhance NADPH generation via G6PD pentose phosphate pathway; consider N-acetylcysteine (NAC) and glycine support." if reductive_capacity_score < 60.0 else "Optimal cellular reductive potential."
    }


def handle_rpc(request_str):
    try:
        req = json.loads(request_str)
        rpc_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})
        
        if method == "tools/list":
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "tools": [{
                        "name": "assess_nadk_nadph_redox_flux",
                        "description": """Assess cellular antioxidant defense through NAD Kinase (NADK) catalytic conversion of NAD+ to NADP+ and the NADPH/NADP+ ratio.
NADPH provides reducing equivalents for glutathione reductase and thioredoxin, neutralizing lipid peroxidation (4-HNE, MDA).
Computes cellular reductive capacity score and flags ferroptosis/oxidative catastrophe vulnerability.""",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    }]
                }
            })
        elif method == "tools/call":
            call_params = params.get("arguments", {})
            res = assess_nadk_nadph_redox_flux(**call_params)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(res, indent=2)
                    }]
                }
            })
        else:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "error": {"code": -32601, "message": f"Method '{method}' not found"}
            })
    except Exception as e:
        return json.dumps({
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32000, "message": str(e)}
        })

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        sample = {'nadk_activity_u_mg': 1.45, 'nadph_umol_l': 18.5, 'nadp_plus_umol_l': 5.2, 'reduced_gsh_to_gssg_ratio': 32.0}
        out = assess_nadk_nadph_redox_flux(**sample)
        print("[TEST_PASS] Output:", json.dumps(out))
    else:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            print(handle_rpc(line))
