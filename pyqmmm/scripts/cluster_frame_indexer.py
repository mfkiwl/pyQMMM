"""Condenses the frame indices of a clustered MD run into a single string"""


def get_clusters(file):
    """
    Get a list of clusters.

    The CPPTraj output file, cnumvtime.dat, is a two column file.
    The first is the frame index and the second is the cluster assignments.
    Parses cnumvtime.dat and creates a list with frames assigned to cluster 0.

    Parameters
    ----------
    file : str
        The location of cnumvtime.dat.

    Returns
    -------
    cluster_list : list[int]
        A list of all frames assigned to the main cluster as integars.

    Example
    -------
    >>> get_clusters("cnumvtime.dat")
    [1,2,3,6,7,8,9,10]

    """
    cluster_list = []
    with open(file, "r") as cluster_file:
        # Skip first line as it is just text
        next(cluster_file)
        for line in cluster_file:
            frame_num = int(line.split()[0])
            cluster_num = int(line.split()[1])
            # Was the frame was assigned to the main cluster, denoted with 0
            if cluster_num == 0:
                cluster_list.append(frame_num)
    return cluster_list


def condense_numbering(cluster_list):
    """
    Simplifies the list of frame indices.

    The list obtained from parsing cnumvtime.dat can contain >100,000 numbers.
    Since CPPTraj accepts interval notation (1,2,3 vs 1-3),
    we can simplify our list of numbers significantly.

    Parameters
    ----------
    cluster_list : list[int]
        A list of the frame indices from the main cluster

    Returns
    -------
    final selection : str
        A string of numbers in interval notation

    Examples
    --------
    >>> condense_numbering([1,2,3,6,7,8,9,10])
    [1-3,6-10]

    """
    # Initialize varibales for later
    seq = []
    final = []
    last = 0

    for index, val in enumerate(cluster_list):
        if last + 1 == val or index == 0:
            seq.append(val)
            last = val
        else:
            if len(seq) > 1:
                final.append(str(seq[0]) + "-" + str(seq[len(seq) - 1]))
            else:
                final.append(str(seq[0]))
            seq = []
            seq.append(val)
            last = val

        if index == len(cluster_list) - 1:
            if len(seq) > 1:
                final.append(str(seq[0]) + "-" + str(seq[len(seq) - 1]))
            else:
                final.append(str(seq[0]))

    final_selection = ", ".join(map(str, final))
    return final_selection


def cluster_frame_indexer():
    """
    Get frames as a simplified string.

    After clustering with CPPTraj, you are returned a cnuvtime.dat file.
    This file contains the frames indices and their corresponding clusters.
    This script finds all frames in the main cluster and condense them into
    the smallest string of numbers. This can then be used as CPPTraj input
    to create a new mdcrd.

    Examples
    --------
    Run the following to generate the CPPTraj output first.

    $ parm welo5_solv.prmtop
    $ trajin constP_prod.mdcrd
    $ trajout output.mdcrd onlyframes 2,5-200,202-400

    Notes
    -----
    Also calculates the interval for 625 snapshots.

    """

    # Provide the user with general info about this utility
    print("\n.-----------------------.")
    print("| CLUSTER FRAME INDEXER |")
    print(".-----------------------.\n")
    print("Run this script in the same directory as cnumvtime.dat.")
    print("The script prints the frame indices.\n")
    print("It will also provide an interval if you want only a subset.\n")

    # This is the standard name but feel free to change it if yours is different
    cluster_definitions_file = "cnumvtime.dat"
    cluster_list = get_clusters(cluster_definitions_file)
    final_selection = condense_numbering(cluster_list)

    # Important output for the user
    print(f"Total frames: {len(cluster_list)}")
    print(f"Final selection: {final_selection}")


if __name__ == "__main__":
    cluster_frame_indexer()