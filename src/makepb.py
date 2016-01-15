from protoboard import ProtoBoard

def singleperf(cols,rows):
    pb = ProtoBoard(cols,rows)
    
    for r in range(rows):
        for c in range(cols):
            pb.addHTrace(c, c, r)
    
    return pb, "single_perf_%d_%d.pb" % (cols,rows)

def doubleperfh(cols, rows):
    pb = ProtoBoard(cols,rows)
    
    for r in range(rows):
        for c in range(0, cols-1, 2):
            pb.addHTrace(c, c+1, r)
            
    if cols % 2 == 1:
        for r in range(rows):
            pb.addHTrace(cols-1, cols-1, r)
    
    return pb, "double_perf_%d_%d_h.pb" % (cols,rows)

def doubleperfv(cols, rows):
    pb = ProtoBoard(cols,rows)
    
    for c in range(cols):
        for r in range(0, rows-1, 2):
            pb.addVTrace(c, r, r+1)
            
    if rows % 2 == 1:
        for c in range(cols):
            pb.addVTrace(c, rows-1, rows-1)
    
    return pb, "double_perf_%d_%d_v.pb" % (cols,rows)

def bpssb300v():
    pb = ProtoBoard(12, 30)
    for r in range(30):
        pb.addHTrace(0, 4, r)
        pb.addHTrace(7, 11, r)
    pb.addVTrace(5, 0, 29)
    pb.addVTrace(6, 0, 29)
    return pb, "bps_sb300_v.pb"

def bpssb300h():
    pb = ProtoBoard(30, 12)
    for c in range(30):
        pb.addVTrace(c, 0, 4)
        pb.addVTrace(c, 7, 11)
    pb.addHTrace(0, 29, 5)
    pb.addHTrace(0, 29, 6)
    return pb, "bps_sb300_h.pb"

def sfbreadboardminiv():
    pb = ProtoBoard(12, 17)
    for r in range(17):
        pb.addHTrace(0, 4, r)
        pb.addHTrace(7, 11, r)
    pb.addVSkip(5)
    pb.addVSkip(6)
    return pb, "sf_breadboard_mini_v.pb"

def sfbreadboardminih():
    pb = ProtoBoard(17, 12)
    for c in range(17):
        pb.addVTrace(c, 0, 4)
        pb.addVTrace(c, 7, 11)
    pb.addHSkip(5)
    pb.addHSkip(6)
    return pb, "sf_breadboard_mini_h.pb"

def adapermaprotoh(n):
    pb = ProtoBoard(n, 18)
    for c in range(n):
        pb.addVTrace(c, 3, 7)
        pb.addVTrace(c, 10, 14)
    pb.addHSkip(2)
    pb.addHSkip(8)
    pb.addHSkip(9)
    pb.addHSkip(15)
    pb.addHTrace(0, n-1, 0)
    pb.addHTrace(0, n-1, 1)
    pb.addHTrace(0, n-1, 16)
    pb.addHTrace(0, n-1, 17)
    return pb, "ada_permaproto_%d_h.pb" % n

def adapermaprotov(n):
    pb = ProtoBoard(18, n)
    for r in range(n):
        pb.addHTrace(3, 7, r)
        pb.addHTrace(10, 14, r)
    pb.addVSkip(2)
    pb.addVSkip(8)
    pb.addVSkip(9)
    pb.addVSkip(15)
    pb.addVTrace(0, 0, n-1)
    pb.addVTrace(1, 0, n-1)
    pb.addVTrace(16, 0, n-1)
    pb.addVTrace(17, 0, n-1)
    return pb, "ada_permaproto_%d_v.pb" % n


pb, fn = doubleperfv(19, 31)      
try:
    fp = open(fn, "w")
    fp.write(pb.getXml())
    fp.write("\n")
    fp.close()
except:
    print "error writing file"