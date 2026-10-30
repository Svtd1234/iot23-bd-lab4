from flask import jsonify, request

from my_project.solar.domain.base import serialize
from my_project.utils.errors import ValidationError


def json_body():
    data = request.get_json(silent=True)
    if data is None:
        raise ValidationError("Тіло запиту має бути коректним JSON (Content-Type: application/json)")
    return data


def pagination():
    values = []
    for name in ("limit", "offset"):
        raw = request.args.get(name)
        if raw is None:
            values.append(None)
            continue
        if not raw.isdigit():
            raise ValidationError(f"Параметр '{name}' має бути невід'ємним цілим числом")
        values.append(int(raw))
    limit, offset = values
    return limit, offset or 0


def row_dto(row, drop=()):
    return {key: serialize(value) for key, value in row.items() if key not in drop}


def children_response(parent_key, parent, children_key, children, row_drop=None):
    if row_drop is None:
        items = [child.to_dto() for child in children]
    else:
        items = [row_dto(child, row_drop) for child in children]
    return jsonify({parent_key: parent.to_dto(), children_key: items}), 200


def grouped_response(pairs, children_key, row_drop=None):
    result = []
    for parent, children in pairs:
        if row_drop is None:
            items = [child.to_dto() for child in children]
        else:
            items = [row_dto(child, row_drop) for child in children]
        result.append({**parent.to_dto(), children_key: items})
    return jsonify(result), 200


class BaseController:
    def __init__(self, service):
        self.service = service

    def get_all(self):
        limit, offset = pagination()
        return jsonify([entity.to_dto() for entity in self.service.get_all(limit, offset)]), 200

    def get_one(self, *pk):
        return jsonify(self.service.get_by_id(*pk).to_dto()), 200

    def create(self):
        return jsonify(self.service.create(json_body()).to_dto()), 201

    def update(self, *pk):
        return jsonify(self.service.update(pk, json_body()).to_dto()), 200

    def delete(self, *pk):
        self.service.delete(*pk)
        return jsonify({"message": f"{self.service.label} з id={'/'.join(str(p) for p in pk)} видалено"}), 200
