from lxml import etree

root = etree.Element("root")
child2 = etree.SubElement(root, "child2")

print(root.tag)
print(len(root))
dic = {1: "a"}
print(dic.get(1))