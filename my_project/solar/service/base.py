from collections import defaultdict

from my_project.utils.errors import NotFoundError, ValidationError


class BaseService:
    dao_class = None
    label = "Запис"

    def __init__(self):
        self.dao = self.dao_class()
        self.entity = self.dao.entity

    def get_all(self, limit=None, offset=0):
        return self.dao.find_all(limit, offset)

    def get_by_id(self, *pk):
        found = self.dao.find_by_id(*pk)
        if found is None:
            raise NotFoundError(f"{self.label} з id={'/'.join(str(p) for p in pk)} не знайдено")
        return found

    def create(self, data):
        values = self.entity.validate(data, partial=False)
        values.update(self.check(dict(values), None) or {})
        pk = self.dao.insert(values)
        created = self.get_by_id(*pk)
        self.after_write(created)
        return created

    def update(self, pk, data):
        current = self.get_by_id(*pk)
        values = self.entity.validate(data, partial=True)
        merged = {**current.values, **values}
        values.update(self.check(merged, current) or {})
        self.dao.update(pk, values)
        updated = self.get_by_id(*pk)
        self.after_write(updated)
        return updated

    def delete(self, *pk):
        self.get_by_id(*pk)
        self.dao.delete(*pk)

    def check(self, values, current):
        return {}

    def after_write(self, entity):
        pass

    def require_exists(self, dao, pk, label):
        if pk is None or not dao.exists(pk):
            raise ValidationError(f"{label} з id={pk} не існує")

    def children_of(self, finder, parent_id):
        parent = self.get_by_id(parent_id)
        return parent, finder(parent_id)

    def with_children(self, child_dao, fk_column):
        grouped = defaultdict(list)
        for child in child_dao.find_all():
            grouped[child.get(fk_column)].append(child)
        return [(parent, grouped.get(parent.pk()[0], [])) for parent in self.dao.find_all()]


def positive(name, value, allow_zero=False):
    if value is None:
        return
    if value < 0 or (value == 0 and not allow_zero):
        raise ValidationError(f"Поле '{name}' має бути {'не менше нуля' if allow_zero else 'більше нуля'}")
