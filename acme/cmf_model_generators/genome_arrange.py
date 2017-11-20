# -*- coding: utf-8 -*-
"""
Created on Nov 17 12:35 2017
@author(s): Florian U. Jehn

Contains all functions needed to clean up a genome
"""
import copy


def find_active_genes(genes, possible_storages):
    """
    Calls all other methods which strip the genes to only the active ones.

    :param genes: Current genes
    :param possible_storages: List of all possible storages
    :return: Copy of current genes, with only the active genes in it.
    """
    # Make a copy, so the original remains unchanged
    genes_copy = copy.deepcopy(genes)
    # Add the first layer to not delete the genes from there as default
    genes_copy += ["first"]
    # Delete all inactive stuff
    genes_copy = del_inactive_storages(genes_copy, possible_storages)
    genes_copy = del_inactive_params(genes_copy, possible_storages)

    return genes_copy


def del_inactive_storages(genes, possible_storages):
    """
    Deletes all storages, which have no inflow from any source.

    :param genes: Current genes
    :param possible_storages: List of all possible storages
    :return: Current genes, with all inactive storages deleted
    """
    # Find all connection genes
    connections = []
    for gene in genes:
        if "tr_" in gene:
            connections.append(gene)

    # Cycle through all connection genes and split them in sources and targets
    sources = []
    targets = []
    for connection in connections:
        name, source, target = connection.split("_")
        sources.append(source)
        targets.append(target)

    # Add snow and canopy if they are present
    if "snow" in genes:
        sources.append("snow")
        targets.append("snow")

    if "canopy" in genes:
        sources.append("canopy")
        targets.append("canopy")

    # Determine which storages are present in the genes
    actual_storages = []
    for possible_storage in possible_storages:
        for gene in genes:
            if possible_storage == gene:
                actual_storages.append(gene)

    # Look if storage is in source and target
    # If not, delete storage
    for storage in actual_storages:
        if storage in targets and storage in sources:
            continue
        else:
            genes.remove(storage)

    return genes


def del_inactive_params(genes, possible_storages):
    """
    Deletes all parameters which do not have their storage present in the
    current genes

    :param genes: Current genes
    :param possible_storages: List of all possible storages
    :return: Current genes, with all inactive params deleted
    """

    # Add the first layer to the copy, so the connections  from first are
    # not all deleted by default.
    # Determine which storages are present in the genes
    actual_storages = ["first"]
    for possible_storage in possible_storages:
        for gene in genes:
            if possible_storage == gene:
                actual_storages.append(gene)

    # Go through all genes to test if their storage is present.
    for gene in genes:
        # Delete all params which do not have their storage present
        storage_present = False
        for storage in actual_storages:
            if storage in gene:
                storage_present = True
                break
        if not storage_present:
            genes.remove(gene)

    return genes


def check_for_connection(genes, possible_connections):
    """
    Determines if a there is a connection to the outlet and if not creates one.

    :param possible_connections: List of all possible connections
    :param genes:
    :return: None
    """
    to_outlet = False
    outgoing = []
    for connection in possible_connections:
        if "out" in connection:
            outgoing.append(connection)
    for connection in outgoing:
        if connection in genes:
            to_outlet = True
            break
    if not to_outlet:
        genes.append("tr_first_out")
