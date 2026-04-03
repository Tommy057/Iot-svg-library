#!/usr/bin/env python3
"""
用法: python3 fix_bindings.py 输入文件.json 输出文件.json
功能: 将每个节点 dataBindings 中绑定的 deviceId 替换为节点自身的 tag
"""
import json, copy, sys

def replace_device_in_binding(binding_block, old_id, new_id):
    b = copy.deepcopy(binding_block)
    d = b['data']
    d['expression'] = d['expression'].replace(old_id, new_id)
    d['replaceOriginalExpression'] = d['replaceOriginalExpression'].replace(old_id, new_id)
    for s in d['source']:
        if s.get('deviceId') == old_id:
            s['deviceId'] = new_id
    for cd in d['checkedData']:
        if cd['key'] == 'device':
            for v in cd['value']:
                if v.get('deviceId') == old_id:
                    v['deviceId'] = new_id
                if v.get('deviceName') == old_id:
                    v['deviceName'] = new_id
    return b

def main():
    if len(sys.argv) < 3:
        print("用法: python3 fix_bindings.py 输入.json 输出.json")
        sys.exit(1)

    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated = 0
    skipped = 0

    for node in data['d']:
        tag = node.get('p', {}).get('tag', '')
        if not tag or tag == 'import':
            continue

        db = node.get('p', {}).get('dataBindings', {}).get('a', {})
        if not db:
            continue

        # 从任意一个绑定中获取当前的 deviceId
        old_id = None
        for attr_binding in db.values():
            sources = attr_binding.get('data', {}).get('source', [])
            if sources:
                old_id = sources[0].get('deviceId')
                break

        if not old_id:
            continue

        if old_id == tag:
            skipped += 1
            print(f"  跳过 {tag}（已正确）")
            continue

        # 替换所有属性绑定中的 deviceId
        for attr_key in list(db.keys()):
            db[attr_key] = replace_device_in_binding(db[attr_key], old_id, tag)

        updated += 1
        print(f"  ✓ {tag}: {old_id} → {tag}")

    print(f"\n共修正 {updated} 个节点，跳过 {skipped} 个（已正确）")

    with open(sys.argv[2], 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"已写出: {sys.argv[2]}")

if __name__ == '__main__':
    main()