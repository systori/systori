from lxml import objectify


def get_text(element):
    concatenated = []
    print("-------------------------------------------")
    for idx, el in enumerate(element.getchildren()):
        print(el.tag)
        print(idx)
        if el.tag is el.getparent().Text:
            print("el.Text")
        #elif el.tag is el.getparent().TextComplement:
        #   print("el.Compl")
        else:
            print("hallo")


def item_info(item):
    print("item_info called")
    name = item.Description.CompleteText.OutlineText.OutlTxt.TextOutlTxt.p.span.text
    description = [get_text(el) for el in item.Description.CompleteText.DetailTxt]
    return name, description

def gaeb_import(filepath):
        tree = objectify.parse(filepath)
        root = tree.getroot()
        label = root.PrjInfo.LblPrj
        for ctgy in root.Award.BoQ.BoQBody.BoQCtgy:
           print("{}".format(ctgy.LblTx.span.text))
           for grp in ctgy.BoQBody.BoQCtgy:
                print("\t{}".format(grp.LblTx.span.text))
                
                for item in grp.BoQBody.Itemlist.getchildren():
                    print(item.get('ID'))
                    task = []
                    task.append(item.Qty.text)
                    task.append(item.QU.text)

                    for text_node in item.Description.CompleteText.DetailTxt.getchildren():
                        task.append(detail_text.span.text)

                    for detail_text in item.Description.CompleteText.DetailTxt:
                        pass
                            #elif child == child.getparent().TextComplement:
                            #    task.append(child.ComplCaption.p.span.text)
                            #    print(task)
        return label

