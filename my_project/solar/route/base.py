def register_crud(bp, path, name, controller, pk_names):
    item_rule = path + "".join(f"/<int:{n}>" for n in pk_names)

    def with_pk(method):
        def view(**kwargs):
            return method(*[kwargs[n] for n in pk_names])

        return view

    bp.add_url_rule(path, f"{name}_list", controller.get_all, methods=["GET"])
    bp.add_url_rule(path, f"{name}_create", controller.create, methods=["POST"])
    bp.add_url_rule(item_rule, f"{name}_get", with_pk(controller.get_one), methods=["GET"])
    bp.add_url_rule(item_rule, f"{name}_update", with_pk(controller.update), methods=["PUT", "PATCH"])
    bp.add_url_rule(item_rule, f"{name}_delete", with_pk(controller.delete), methods=["DELETE"])


def register_view(bp, rule, endpoint, method):
    def view(**kwargs):
        return method(**kwargs)

    bp.add_url_rule(rule, endpoint, view, methods=["GET"])
