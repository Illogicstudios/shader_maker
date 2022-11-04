
# Clear a layout recusrively
def clear_layout(layout):
    children = []
    for i in range(layout.count()):
        child = layout.itemAt(i).widget()
        if not child:
            clear_layout(layout.itemAt(i).layout())
        else:
            children.append(child)
    for child in children:
        child.deleteLater()