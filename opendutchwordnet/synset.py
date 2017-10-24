from .relation import Relation

# import xml parser (lxml is preferred, else built-in module xml is used)
try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree


class Synset(object):
    """
    Class for XML element Synset.

    example of Synset element:
    <Synset id="eng-30-00324560-v" ili="i23355">
    <Definition gloss="cook with dry heat, usually in an oven" language="en" provenance="pwn"/>
    <SynsetRelations>
        <SynsetRelation provenance="pwn" relType="has_hyperonym" target="eng-30-00322847-v"/>
        <SynsetRelation provenance="pwn" relType="has_hyponym" target="eng-30-00325085-v"/>
    </SynsetRelations>
    </Synset>

    """

    def __init__(self, synset_el, reltypes, syn_ids):

        self.synset_el = synset_el
        self.reltypes = reltypes
        self.syn_ids = syn_ids

        self.defs_els = self.synset_el.find("Definitions")
        self.refs_el = self.synset_el.find("SynsetRelations")

    def id(self):
        """
        Return synset identifier.

        @rtype: str
        @return: synset identifier
        """
        return self.synset_el.get("id")

    def ili(self):
        """
        Return gwg ili by returning value of attribute "ili".

        @rtype: str
        @return: global wordnet grid ili
        """
        return self.synset_el.get("ili")

    def glosses(self, languages=('en', 'nl')):
        """
        Get gloss of synset by returning value of attribute "gloss".

        @rtype: generator
        @return: generator of synset definitions
        """
        if self.defs_els is not None:
            return [def_el.get('gloss')
                    for def_el in self.defs_els.iterfind("Definition")
                    if def_el.get('language') in languages]
        else:
            return []

    def all_relations(self):
        """
        Return list of instances of class Relation.

        @rtype: generator
        @return: generator of instances of class Relation
        """
        path_to_rels = "SynsetRelations/SynsetRelation"
        for relation_el in self.synset_el.iterfind(path_to_rels):
            yield Relation(relation_el)

    def pos(self):
        """
        return pos (last charachter of ili)

        @rtype: str
        @return: pos
        """
        return self.id()[-1]

    def relations(self, reltype):
        """
        return list of instance of class Relations that match the relation type

        @type   reltype: str
        @param: reltype: relation type (most typical are has_hyperonym and
        has_hyponym

        @rtype: list
        @return: list of instances of class Relation
        """
        xml_query="""SynsetRelations/SynsetRelation[@relType="%s"]""" % reltype
        return [Relation(relation_el)
                for relation_el in self.synset_el.iterfind(xml_query)]

    def remove(self):
        """Remove synset element."""
        self.synset_el.getparent().remove(self.synset_el)

    def add_relation(self, reltype, target):
        """
        Add a SynsetRelation.

        <SynsetRelation provenance="pwn" relType="has_hyponym" target="eng-30-00325085-v"/>

        @type  reltype: str
        @param reltype: type of relation

        @type target: str
        @param target: target synset

        @rtype: tuple
        @return: (succes, message)

        """
        source = self.id()
        self.validate_relation(source, reltype, target)

        existing_rels = [(rel_el.get_reltype(), rel_el.get_target())
                         for rel_el in self.all_relations()]

        if (reltype, target) in existing_rels:
            raise ValueError("relation already exists")

        # add SynsetRelations element if it does not exists
        if self.refs_el is None:
            new_refs_el = etree.SubElement(self.synset_el, "SynsetRelations")
            self.synset_el.append(new_refs_el)

        # add SynsetRelations element
        new_rel_el = etree.SubElement(self.synset_el,
                                      "SynsetRelation",
                                      {'provenance': 'odwn',
                                       'relType': reltype,
                                       'target': target})
        self.refs_el.append(new_rel_el)
