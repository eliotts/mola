from copy import deepcopy as _deepcopy
import math as _math
import mola.vec as _vec

class MCube:
  
  def __init__(self):
    self.xc = []
    self.yc = []
    self.zc = []
    self.triangles = []

    #babylon structure
    self.positions = []
    self.indices = []
    
    self.faces = self._getFaces()
     
  def marchingCubesMeshFromVoxelSpace(self,vs,iso):
    return self.marchingCubesMesh(vs.nX,vs.nY,vs.nZ,vs.values,iso,1,-vs.nX/2.0,-vs.nY/2.0,-vs.nZ/2.0)
	
              
  def marchingCubesMesh(self, nX, nY, nZ, values, iso, scale, tX, tY, tZ):     
    mesh = Mesh()
              
    nYZ = nY*nZ
    nVs = 0
    index = 0

    vertices = []

    nbs = [0]*8
    edges = [0]*12
      
    xEdges = [[0 for x in range(nY)] for y in range(nZ)]
    yEdges = [[0 for x in range(nY)] for y in range(nZ)]
    zEdges = [[0 for x in range(nY)] for y in range(nZ)]
    yEdgesUp = [[0 for x in range(nY)] for y in range(nZ)]
    zEdgesUp = [[0 for x in range(nY)] for y in range(nZ)]
      
    for x in range(nX-1):
      if(x==0):
        for y in range(nY):
          for z in range(nZ):
            index = z + y * nZ + x * nYZ
            cV = values[index]
            if(y<nY-1):
              yNb = values[index + nZ]
              if(self._isBorder(cV,yNb,iso)):
                vertex = [x,self._getValue(iso,cV,yNb)+y,z]
                vertices.append(vertex)
                yEdges[y][z] = nVs
                nVs+=1
            if(z<nZ-1):
              zNb = values[index + 1]
              if(self._isBorder(cV,zNb,iso)):
                vertex = [x,y,self._getValue(iso,cV,zNb)+z]
                vertices.append(vertex)
                zEdges[y][z] = nVs
                nVs+=1
      else:
        yEdges = _deepcopy(yEdgesUp)
        zEdges = _deepcopy(zEdgesUp)
      
            
      for y in range(nY):
        for z in range(nZ):
          index = z+y*nZ+x*nYZ
          cV = values[index]
          xNb = values[index+nYZ]
          if(self._isBorder(cV,xNb,iso)):
            vertex = Vertex(self._getValue(iso,cV,xNb)+x,y,z)
            vertex = _vec.VectorAdd(_vec.VectorScale(vertex,scale),Vertex(tX,tY,tZ))
            vertices.append(vertex)
            xEdges[y][z] = nVs
            nVs+=1
          index+=nYZ
          cV = values[index]
          if(y<nY-1):
            yNb = values[index+nZ]
            if(self._isBorder(cV,yNb,iso)):
              vertex = Vertex(x+1,self._getValue(iso,cV,yNb)+y,z)
              vertex = _vec.VectorAdd(_vec.VectorScale(vertex,scale),Vertex(tX,tY,tZ))
              vertices.append(vertex)
              yEdgesUp[y][z] = nVs
              nVs+=1
          if(z<nZ-1):
            zNb = values[index+1]
            if(self._isBorder(cV,zNb,iso)):
              vertex = Vertex(x+1,y,self._getValue(iso,cV,zNb)+z)
              vertex = _vec.VectorAdd(_vec.VectorScale(vertex,scale),Vertex(tX,tY,tZ))
              vertices.append(vertex)
              zEdgesUp[y][z] = nVs
              nVs+=1
      
      for v in vertices:
              v.id = -1 
              
      #collecting the faces
      for y in range(nY-1):
        for z in range(nZ-1):
          caseNumber = 0
          index = z+y*nZ+x*nYZ
          nbs[0] = values[index+nZ]
          nbs[1] = values[index + nYZ + nZ];
          nbs[2] = values[index + nYZ];
          nbs[3] = values[index];
          nbs[4] = values[index + nZ + 1];
          nbs[5] = values[index + nYZ + nZ + 1];
          nbs[6] = values[index + nYZ + 1];
          nbs[7] = values[index + 1];
      
          for i in reversed(range(8)):
            if(nbs[i]>iso):
              caseNumber+=1
            if(i>0):
              caseNumber = caseNumber << 1
  
          edges[0] = xEdges[y + 1][z];
          edges[1] = yEdgesUp[y][z];
          edges[2] = xEdges[y][z];
          edges[3] = yEdges[y][z];

          edges[4] = xEdges[y + 1][z + 1];
          edges[5] = yEdgesUp[y][z + 1];
          edges[6] = xEdges[y][z + 1];
          edges[7] = yEdges[y][z + 1];

          edges[8] = zEdges[y + 1][z];
          edges[9] = zEdgesUp[y + 1][z];
          edges[10] = zEdges[y][z];
          edges[11] = zEdgesUp[y][z];

          offset = caseNumber * 15
      
          for i in range(offset,offset+15,3):
            if(self.faces[i]>-1):
              
              facePoints = []
              
              for j in range(i,i+3,1):
                v0 = edges[self.faces[j]]
                v = vertices[v0]
                if(v.id<0):
                  v.id = len(mesh.vertices)-1
                facePoints.append(v)
                
              face = Face(facePoints)
              if(len(facePoints)==3):
                mesh.faces.append(face)

    return mesh
                   
    
  def marchingCubes(self, nX, nY, nZ, values, iso, scale, tX, tY, tZ):            
    nYZ = nY*nZ
    nVs = 0
    index = 0
      
    triangleList = []
    vertices = []

    nbs = [0]*8
    edges = [0]*12
      
    xEdges = [[0 for x in range(nY)] for y in range(nZ)]
    yEdges = [[0 for x in range(nY)] for y in range(nZ)]
    zEdges = [[0 for x in range(nY)] for y in range(nZ)]
    yEdgesUp = [[0 for x in range(nY)] for y in range(nZ)]
    zEdgesUp = [[0 for x in range(nY)] for y in range(nZ)]
      
    for x in range(nX-1):
      if(x==0):
        for y in range(nY):
          for z in range(nZ):
            index = z + y * nZ + x * nYZ
            cV = values[index]
            if(y<nY-1):
              yNb = values[index + nZ]
              if(self._isBorder(cV,yNb,iso)):
                vertex = [x,self._getValue(iso,cV,yNb)+y,z]
                vertices.append(vertex)
                yEdges[y][z] = nVs
                nVs+=1
            if(z<nZ-1):
              zNb = values[index + 1]
              if(self._isBorder(cV,zNb,iso)):
                vertex = [x,y,self._getValue(iso,cV,zNb)+z]
                vertices.append(vertex)
                zEdges[y][z] = nVs
                nVs+=1
      else:
        yEdges = _deepcopy(yEdgesUp)
        zEdges = _deepcopy(zEdgesUp)
      
      for y in range(nY):
        for z in range(nZ):
          index = z+y*nZ+x*nYZ
          cV = values[index]
          xNb = values[index+nYZ]
          if(self._isBorder(cV,xNb,iso)):
            vertex = [self._getValue(iso,cV,xNb)+x,y,z]
            vertices.append(vertex)
            xEdges[y][z] = nVs
            nVs+=1
          index+=nYZ
          cV = values[index]
          if(y<nY-1):
            yNb = values[index+nZ]
            if(self._isBorder(cV,yNb,iso)):
              vertex = [x+1,self._getValue(iso,cV,yNb)+y,z]
              vertices.append(vertex)
              yEdgesUp[y][z] = nVs
              nVs+=1
          if(z<nZ-1):
            zNb = values[index+1]
            if(self._isBorder(cV,zNb,iso)):
              vertex = [x+1,y,self._getValue(iso,cV,zNb)+z]
              vertices.append(vertex)
              zEdgesUp[y][z] = nVs
              nVs+=1
      
      #collecting the faces
      for y in range(nY-1):
        for z in range(nZ-1):
          caseNumber = 0
          index = z+y*nZ+x*nYZ
          nbs[0] = values[index+nZ]
          nbs[1] = values[index + nYZ + nZ];
          nbs[2] = values[index + nYZ];
          nbs[3] = values[index];
          nbs[4] = values[index + nZ + 1];
          nbs[5] = values[index + nYZ + nZ + 1];
          nbs[6] = values[index + nYZ + 1];
          nbs[7] = values[index + 1];
      
          for i in reversed(range(8)):
            if(nbs[i]>iso):
              caseNumber+=1
            if(i>0):
              caseNumber = caseNumber << 1
  
          edges[0] = xEdges[y + 1][z];
          edges[1] = yEdgesUp[y][z];
          edges[2] = xEdges[y][z];
          edges[3] = yEdges[y][z];

          edges[4] = xEdges[y + 1][z + 1];
          edges[5] = yEdgesUp[y][z + 1];
          edges[6] = xEdges[y][z + 1];
          edges[7] = yEdges[y][z + 1];

          edges[8] = zEdges[y + 1][z];
          edges[9] = zEdgesUp[y + 1][z];
          edges[10] = zEdges[y][z];
          edges[11] = zEdgesUp[y][z];

          offset = caseNumber * 15
      
          for i in range(offset,offset+15,3):
            if(self.faces[i]>-1):
              v0 = edges[self.faces[i]]
              v1 = edges[self.faces[i+1]]
              v2 = edges[self.faces[i+2]]
              triangle = [v0,v1,v2]
              triangleList.append(v0)
              triangleList.append(v1)
              triangleList.append(v2)
      
    self.output(vertices,triangleList,scale,tX,tY,tZ)
      
  def output(self, vertices, triangleList, scale, tX, tY, tZ):
    for v in vertices:
      v[0] = v[0] * scale + tX
      v[1] = v[1] * scale + tY
      v[2] = v[2] * scale + tZ
      
    self.xc = []
    self.yc = []
    self.zc = []
      
    for v in vertices:
      self.xc.append(v[0])
      self.yc.append(v[1])
      self.zc.append(v[2])
      
    self.triangles = []
      
    for triangle in triangleList:
      for i in range(3):
        self.triangles.append(triangle[i])
    triangleList = []
    vertices = []
      
      
  def _getValue(self, iso,v1,v2):
      if(_math.fabs(v2-v1)<0.0001):
        return 0
      else:
        return ((iso-v1)/(v2-v1))
      
  def _isBorder(self, v1,v2,iso):
      if(v1>iso and v2<=iso):
        return True
      if(v2>iso and v1<=iso):
        return True
      return False


  def _getFaces(self):
    return [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
         -1, -1, -1, -1, 0, 8, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
        -1, -1, 0, 1, 9, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1,
        8, 3, 9, 8, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 2, 11, -1,
        -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 8, 3, 1, 2, 11, -1,
        -1, -1, -1, -1, -1, -1, -1, -1, 9, 2, 11, 0, 2, 9, -1, -1, -1, -1,
        -1, -1, -1, -1, -1, 2, 8, 3, 2, 11, 8, 11, 9, 8, -1, -1, -1, -1,
        -1, -1, 3, 10, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
        0, 10, 2, 8, 10, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 9, 0, 2,
        3, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 10, 2, 1, 9, 10, 9,
        8, 10, -1, -1, -1, -1, -1, -1, 3, 11, 1, 10, 11, 3, -1, -1, -1, -1,
        -1, -1, -1, -1, -1, 0, 11, 1, 0, 8, 11, 8, 10, 11, -1, -1, -1, -1,
        -1, -1, 3, 9, 0, 3, 10, 9, 10, 11, 9, -1, -1, -1, -1, -1, -1, 9, 8,
        11, 11, 8, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, 4, 7, 8, -1, -1,
        -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 4, 3, 0, 7, 3, 4, -1, -1,
        -1, -1, -1, -1, -1, -1, -1, 0, 1, 9, 8, 4, 7, -1, -1, -1, -1, -1,
        -1, -1, -1, -1, 4, 1, 9, 4, 7, 1, 7, 3, 1, -1, -1, -1, -1, -1, -1,
        1, 2, 11, 8, 4, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, 3, 4, 7, 3,
        0, 4, 1, 2, 11, -1, -1, -1, -1, -1, -1, 9, 2, 11, 9, 0, 2, 8, 4, 7,
        -1, -1, -1, -1, -1, -1, 2, 11, 9, 2, 9, 7, 2, 7, 3, 7, 9, 4, -1,
        -1, -1, 8, 4, 7, 3, 10, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, 10,
        4, 7, 10, 2, 4, 2, 0, 4, -1, -1, -1, -1, -1, -1, 9, 0, 1, 8, 4, 7,
        2, 3, 10, -1, -1, -1, -1, -1, -1, 4, 7, 10, 9, 4, 10, 9, 10, 2, 9,
        2, 1, -1, -1, -1, 3, 11, 1, 3, 10, 11, 7, 8, 4, -1, -1, -1, -1, -1,
        -1, 1, 10, 11, 1, 4, 10, 1, 0, 4, 7, 10, 4, -1, -1, -1, 4, 7, 8, 9,
        0, 10, 9, 10, 11, 10, 0, 3, -1, -1, -1, 4, 7, 10, 4, 10, 9, 9, 10,
        11, -1, -1, -1, -1, -1, -1, 9, 5, 4, -1, -1, -1, -1, -1, -1, -1,
        -1, -1, -1, -1, -1, 9, 5, 4, 0, 8, 3, -1, -1, -1, -1, -1, -1, -1,
        -1, -1, 0, 5, 4, 1, 5, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, 8, 5,
        4, 8, 3, 5, 3, 1, 5, -1, -1, -1, -1, -1, -1, 1, 2, 11, 9, 5, 4, -1,
        -1, -1, -1, -1, -1, -1, -1, -1, 3, 0, 8, 1, 2, 11, 4, 9, 5, -1, -1,
        -1, -1, -1, -1, 5, 2, 11, 5, 4, 2, 4, 0, 2, -1, -1, -1, -1, -1, -1,
        2, 11, 5, 3, 2, 5, 3, 5, 4, 3, 4, 8, -1, -1, -1, 9, 5, 4, 2, 3, 10,
        -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 10, 2, 0, 8, 10, 4, 9, 5,
        -1, -1, -1, -1, -1, -1, 0, 5, 4, 0, 1, 5, 2, 3, 10, -1, -1, -1, -1,
        -1, -1, 2, 1, 5, 2, 5, 8, 2, 8, 10, 4, 8, 5, -1, -1, -1, 11, 3, 10,
        11, 1, 3, 9, 5, 4, -1, -1, -1, -1, -1, -1, 4, 9, 5, 0, 8, 1, 8, 11,
        1, 8, 10, 11, -1, -1, -1, 5, 4, 0, 5, 0, 10, 5, 10, 11, 10, 0, 3,
        -1, -1, -1, 5, 4, 8, 5, 8, 11, 11, 8, 10, -1, -1, -1, -1, -1, -1,
        9, 7, 8, 5, 7, 9, -1, -1, -1, -1, -1, -1, -1, -1, -1, 9, 3, 0, 9,
        5, 3, 5, 7, 3, -1, -1, -1, -1, -1, -1, 0, 7, 8, 0, 1, 7, 1, 5, 7,
        -1, -1, -1, -1, -1, -1, 1, 5, 3, 3, 5, 7, -1, -1, -1, -1, -1, -1,
        -1, -1, -1, 9, 7, 8, 9, 5, 7, 11, 1, 2, -1, -1, -1, -1, -1, -1, 11,
        1, 2, 9, 5, 0, 5, 3, 0, 5, 7, 3, -1, -1, -1, 8, 0, 2, 8, 2, 5, 8,
        5, 7, 11, 5, 2, -1, -1, -1, 2, 11, 5, 2, 5, 3, 3, 5, 7, -1, -1, -1,
        -1, -1, -1, 7, 9, 5, 7, 8, 9, 3, 10, 2, -1, -1, -1, -1, -1, -1, 9,
        5, 7, 9, 7, 2, 9, 2, 0, 2, 7, 10, -1, -1, -1, 2, 3, 10, 0, 1, 8, 1,
        7, 8, 1, 5, 7, -1, -1, -1, 10, 2, 1, 10, 1, 7, 7, 1, 5, -1, -1, -1,
        -1, -1, -1, 9, 5, 8, 8, 5, 7, 11, 1, 3, 11, 3, 10, -1, -1, -1, 5,
        7, 0, 5, 0, 9, 7, 10, 0, 1, 0, 11, 10, 11, 0, 10, 11, 0, 10, 0, 3,
        11, 5, 0, 8, 0, 7, 5, 7, 0, 10, 11, 5, 7, 10, 5, -1, -1, -1, -1,
        -1, -1, -1, -1, -1, 11, 6, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1,
        -1, -1, -1, 0, 8, 3, 5, 11, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1,
        9, 0, 1, 5, 11, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 8, 3, 1,
        9, 8, 5, 11, 6, -1, -1, -1, -1, -1, -1, 1, 6, 5, 2, 6, 1, -1, -1,
        -1, -1, -1, -1, -1, -1, -1, 1, 6, 5, 1, 2, 6, 3, 0, 8, -1, -1, -1,
        -1, -1, -1, 9, 6, 5, 9, 0, 6, 0, 2, 6, -1, -1, -1, -1, -1, -1, 5,
        9, 8, 5, 8, 2, 5, 2, 6, 3, 2, 8, -1, -1, -1, 2, 3, 10, 11, 6, 5,
        -1, -1, -1, -1, -1, -1, -1, -1, -1, 10, 0, 8, 10, 2, 0, 11, 6, 5,
        -1, -1, -1, -1, -1, -1, 0, 1, 9, 2, 3, 10, 5, 11, 6, -1, -1, -1,
        -1, -1, -1, 5, 11, 6, 1, 9, 2, 9, 10, 2, 9, 8, 10, -1, -1, -1, 6,
        3, 10, 6, 5, 3, 5, 1, 3, -1, -1, -1, -1, -1, -1, 0, 8, 10, 0, 10,
        5, 0, 5, 1, 5, 10, 6, -1, -1, -1, 3, 10, 6, 0, 3, 6, 0, 6, 5, 0, 5,
        9, -1, -1, -1, 6, 5, 9, 6, 9, 10, 10, 9, 8, -1, -1, -1, -1, -1, -1,
        5, 11, 6, 4, 7, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, 4, 3, 0, 4,
        7, 3, 6, 5, 11, -1, -1, -1, -1, -1, -1, 1, 9, 0, 5, 11, 6, 8, 4, 7,
        -1, -1, -1, -1, -1, -1, 11, 6, 5, 1, 9, 7, 1, 7, 3, 7, 9, 4, -1,
        -1, -1, 6, 1, 2, 6, 5, 1, 4, 7, 8, -1, -1, -1, -1, -1, -1, 1, 2, 5,
        5, 2, 6, 3, 0, 4, 3, 4, 7, -1, -1, -1, 8, 4, 7, 9, 0, 5, 0, 6, 5,
        0, 2, 6, -1, -1, -1, 7, 3, 9, 7, 9, 4, 3, 2, 9, 5, 9, 6, 2, 6, 9,
        3, 10, 2, 7, 8, 4, 11, 6, 5, -1, -1, -1, -1, -1, -1, 5, 11, 6, 4,
        7, 2, 4, 2, 0, 2, 7, 10, -1, -1, -1, 0, 1, 9, 4, 7, 8, 2, 3, 10, 5,
        11, 6, -1, -1, -1, 9, 2, 1, 9, 10, 2, 9, 4, 10, 7, 10, 4, 5, 11, 6,
        8, 4, 7, 3, 10, 5, 3, 5, 1, 5, 10, 6, -1, -1, -1, 5, 1, 10, 5, 10,
        6, 1, 0, 10, 7, 10, 4, 0, 4, 10, 0, 5, 9, 0, 6, 5, 0, 3, 6, 10, 6,
        3, 8, 4, 7, 6, 5, 9, 6, 9, 10, 4, 7, 9, 7, 10, 9, -1, -1, -1, 11,
        4, 9, 6, 4, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, 4, 11, 6, 4, 9,
        11, 0, 8, 3, -1, -1, -1, -1, -1, -1, 11, 0, 1, 11, 6, 0, 6, 4, 0,
        -1, -1, -1, -1, -1, -1, 8, 3, 1, 8, 1, 6, 8, 6, 4, 6, 1, 11, -1,
        -1, -1, 1, 4, 9, 1, 2, 4, 2, 6, 4, -1, -1, -1, -1, -1, -1, 3, 0, 8,
        1, 2, 9, 2, 4, 9, 2, 6, 4, -1, -1, -1, 0, 2, 4, 4, 2, 6, -1, -1,
        -1, -1, -1, -1, -1, -1, -1, 8, 3, 2, 8, 2, 4, 4, 2, 6, -1, -1, -1,
        -1, -1, -1, 11, 4, 9, 11, 6, 4, 10, 2, 3, -1, -1, -1, -1, -1, -1,
        0, 8, 2, 2, 8, 10, 4, 9, 11, 4, 11, 6, -1, -1, -1, 3, 10, 2, 0, 1,
        6, 0, 6, 4, 6, 1, 11, -1, -1, -1, 6, 4, 1, 6, 1, 11, 4, 8, 1, 2, 1,
        10, 8, 10, 1, 9, 6, 4, 9, 3, 6, 9, 1, 3, 10, 6, 3, -1, -1, -1, 8,
        10, 1, 8, 1, 0, 10, 6, 1, 9, 1, 4, 6, 4, 1, 3, 10, 6, 3, 6, 0, 0,
        6, 4, -1, -1, -1, -1, -1, -1, 6, 4, 8, 10, 6, 8, -1, -1, -1, -1,
        -1, -1, -1, -1, -1, 7, 11, 6, 7, 8, 11, 8, 9, 11, -1, -1, -1, -1,
        -1, -1, 0, 7, 3, 0, 11, 7, 0, 9, 11, 6, 7, 11, -1, -1, -1, 11, 6,
        7, 1, 11, 7, 1, 7, 8, 1, 8, 0, -1, -1, -1, 11, 6, 7, 11, 7, 1, 1,
        7, 3, -1, -1, -1, -1, -1, -1, 1, 2, 6, 1, 6, 8, 1, 8, 9, 8, 6, 7,
        -1, -1, -1, 2, 6, 9, 2, 9, 1, 6, 7, 9, 0, 9, 3, 7, 3, 9, 7, 8, 0,
        7, 0, 6, 6, 0, 2, -1, -1, -1, -1, -1, -1, 7, 3, 2, 6, 7, 2, -1, -1,
        -1, -1, -1, -1, -1, -1, -1, 2, 3, 10, 11, 6, 8, 11, 8, 9, 8, 6, 7,
        -1, -1, -1, 2, 0, 7, 2, 7, 10, 0, 9, 7, 6, 7, 11, 9, 11, 7, 1, 8,
        0, 1, 7, 8, 1, 11, 7, 6, 7, 11, 2, 3, 10, 10, 2, 1, 10, 1, 7, 11,
        6, 1, 6, 7, 1, -1, -1, -1, 8, 9, 6, 8, 6, 7, 9, 1, 6, 10, 6, 3, 1,
        3, 6, 0, 9, 1, 10, 6, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, 7, 8,
        0, 7, 0, 6, 3, 10, 0, 10, 6, 0, -1, -1, -1, 7, 10, 6, -1, -1, -1,
        -1, -1, -1, -1, -1, -1, -1, -1, -1, 7, 6, 10, -1, -1, -1, -1, -1,
        -1, -1, -1, -1, -1, -1, -1, 3, 0, 8, 10, 7, 6, -1, -1, -1, -1, -1,
        -1, -1, -1, -1, 0, 1, 9, 10, 7, 6, -1, -1, -1, -1, -1, -1, -1, -1,
        -1, 8, 1, 9, 8, 3, 1, 10, 7, 6, -1, -1, -1, -1, -1, -1, 11, 1, 2,
        6, 10, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 2, 11, 3, 0, 8, 6,
        10, 7, -1, -1, -1, -1, -1, -1, 2, 9, 0, 2, 11, 9, 6, 10, 7, -1, -1,
        -1, -1, -1, -1, 6, 10, 7, 2, 11, 3, 11, 8, 3, 11, 9, 8, -1, -1, -1,
        7, 2, 3, 6, 2, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, 7, 0, 8, 7,
        6, 0, 6, 2, 0, -1, -1, -1, -1, -1, -1, 2, 7, 6, 2, 3, 7, 0, 1, 9,
        -1, -1, -1, -1, -1, -1, 1, 6, 2, 1, 8, 6, 1, 9, 8, 8, 7, 6, -1, -1,
        -1, 11, 7, 6, 11, 1, 7, 1, 3, 7, -1, -1, -1, -1, -1, -1, 11, 7, 6,
        1, 7, 11, 1, 8, 7, 1, 0, 8, -1, -1, -1, 0, 3, 7, 0, 7, 11, 0, 11,
        9, 6, 11, 7, -1, -1, -1, 7, 6, 11, 7, 11, 8, 8, 11, 9, -1, -1, -1,
        -1, -1, -1, 6, 8, 4, 10, 8, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1,
        3, 6, 10, 3, 0, 6, 0, 4, 6, -1, -1, -1, -1, -1, -1, 8, 6, 10, 8, 4,
        6, 9, 0, 1, -1, -1, -1, -1, -1, -1, 9, 4, 6, 9, 6, 3, 9, 3, 1, 10,
        3, 6, -1, -1, -1, 6, 8, 4, 6, 10, 8, 2, 11, 1, -1, -1, -1, -1, -1,
        -1, 1, 2, 11, 3, 0, 10, 0, 6, 10, 0, 4, 6, -1, -1, -1, 4, 10, 8, 4,
        6, 10, 0, 2, 9, 2, 11, 9, -1, -1, -1, 11, 9, 3, 11, 3, 2, 9, 4, 3,
        10, 3, 6, 4, 6, 3, 8, 2, 3, 8, 4, 2, 4, 6, 2, -1, -1, -1, -1, -1,
        -1, 0, 4, 2, 4, 6, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 9, 0,
        2, 3, 4, 2, 4, 6, 4, 3, 8, -1, -1, -1, 1, 9, 4, 1, 4, 2, 2, 4, 6,
        -1, -1, -1, -1, -1, -1, 8, 1, 3, 8, 6, 1, 8, 4, 6, 6, 11, 1, -1,
        -1, -1, 11, 1, 0, 11, 0, 6, 6, 0, 4, -1, -1, -1, -1, -1, -1, 4, 6,
        3, 4, 3, 8, 6, 11, 3, 0, 3, 9, 11, 9, 3, 11, 9, 4, 6, 11, 4, -1,
        -1, -1, -1, -1, -1, -1, -1, -1, 4, 9, 5, 7, 6, 10, -1, -1, -1, -1,
        -1, -1, -1, -1, -1, 0, 8, 3, 4, 9, 5, 10, 7, 6, -1, -1, -1, -1, -1,
        -1, 5, 0, 1, 5, 4, 0, 7, 6, 10, -1, -1, -1, -1, -1, -1, 10, 7, 6,
        8, 3, 4, 3, 5, 4, 3, 1, 5, -1, -1, -1, 9, 5, 4, 11, 1, 2, 7, 6, 10,
        -1, -1, -1, -1, -1, -1, 6, 10, 7, 1, 2, 11, 0, 8, 3, 4, 9, 5, -1,
        -1, -1, 7, 6, 10, 5, 4, 11, 4, 2, 11, 4, 0, 2, -1, -1, -1, 3, 4, 8,
        3, 5, 4, 3, 2, 5, 11, 5, 2, 10, 7, 6, 7, 2, 3, 7, 6, 2, 5, 4, 9,
        -1, -1, -1, -1, -1, -1, 9, 5, 4, 0, 8, 6, 0, 6, 2, 6, 8, 7, -1, -1,
        -1, 3, 6, 2, 3, 7, 6, 1, 5, 0, 5, 4, 0, -1, -1, -1, 6, 2, 8, 6, 8,
        7, 2, 1, 8, 4, 8, 5, 1, 5, 8, 9, 5, 4, 11, 1, 6, 1, 7, 6, 1, 3, 7,
        -1, -1, -1, 1, 6, 11, 1, 7, 6, 1, 0, 7, 8, 7, 0, 9, 5, 4, 4, 0, 11,
        4, 11, 5, 0, 3, 11, 6, 11, 7, 3, 7, 11, 7, 6, 11, 7, 11, 8, 5, 4,
        11, 4, 8, 11, -1, -1, -1, 6, 9, 5, 6, 10, 9, 10, 8, 9, -1, -1, -1,
        -1, -1, -1, 3, 6, 10, 0, 6, 3, 0, 5, 6, 0, 9, 5, -1, -1, -1, 0, 10,
        8, 0, 5, 10, 0, 1, 5, 5, 6, 10, -1, -1, -1, 6, 10, 3, 6, 3, 5, 5,
        3, 1, -1, -1, -1, -1, -1, -1, 1, 2, 11, 9, 5, 10, 9, 10, 8, 10, 5,
        6, -1, -1, -1, 0, 10, 3, 0, 6, 10, 0, 9, 6, 5, 6, 9, 1, 2, 11, 10,
        8, 5, 10, 5, 6, 8, 0, 5, 11, 5, 2, 0, 2, 5, 6, 10, 3, 6, 3, 5, 2,
        11, 3, 11, 5, 3, -1, -1, -1, 5, 8, 9, 5, 2, 8, 5, 6, 2, 3, 8, 2,
        -1, -1, -1, 9, 5, 6, 9, 6, 0, 0, 6, 2, -1, -1, -1, -1, -1, -1, 1,
        5, 8, 1, 8, 0, 5, 6, 8, 3, 8, 2, 6, 2, 8, 1, 5, 6, 2, 1, 6, -1, -1,
        -1, -1, -1, -1, -1, -1, -1, 1, 3, 6, 1, 6, 11, 3, 8, 6, 5, 6, 9, 8,
        9, 6, 11, 1, 0, 11, 0, 6, 9, 5, 0, 5, 6, 0, -1, -1, -1, 0, 3, 8, 5,
        6, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, 11, 5, 6, -1, -1, -1,
        -1, -1, -1, -1, -1, -1, -1, -1, -1, 10, 5, 11, 7, 5, 10, -1, -1,
        -1, -1, -1, -1, -1, -1, -1, 10, 5, 11, 10, 7, 5, 8, 3, 0, -1, -1,
        -1, -1, -1, -1, 5, 10, 7, 5, 11, 10, 1, 9, 0, -1, -1, -1, -1, -1,
        -1, 11, 7, 5, 11, 10, 7, 9, 8, 1, 8, 3, 1, -1, -1, -1, 10, 1, 2,
        10, 7, 1, 7, 5, 1, -1, -1, -1, -1, -1, -1, 0, 8, 3, 1, 2, 7, 1, 7,
        5, 7, 2, 10, -1, -1, -1, 9, 7, 5, 9, 2, 7, 9, 0, 2, 2, 10, 7, -1,
        -1, -1, 7, 5, 2, 7, 2, 10, 5, 9, 2, 3, 2, 8, 9, 8, 2, 2, 5, 11, 2,
        3, 5, 3, 7, 5, -1, -1, -1, -1, -1, -1, 8, 2, 0, 8, 5, 2, 8, 7, 5,
        11, 2, 5, -1, -1, -1, 9, 0, 1, 5, 11, 3, 5, 3, 7, 3, 11, 2, -1, -1,
        -1, 9, 8, 2, 9, 2, 1, 8, 7, 2, 11, 2, 5, 7, 5, 2, 1, 3, 5, 3, 7, 5,
        -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 8, 7, 0, 7, 1, 1, 7, 5, -1,
        -1, -1, -1, -1, -1, 9, 0, 3, 9, 3, 5, 5, 3, 7, -1, -1, -1, -1, -1,
        -1, 9, 8, 7, 5, 9, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, 5, 8, 4,
        5, 11, 8, 11, 10, 8, -1, -1, -1, -1, -1, -1, 5, 0, 4, 5, 10, 0, 5,
        11, 10, 10, 3, 0, -1, -1, -1, 0, 1, 9, 8, 4, 11, 8, 11, 10, 11, 4,
        5, -1, -1, -1, 11, 10, 4, 11, 4, 5, 10, 3, 4, 9, 4, 1, 3, 1, 4, 2,
        5, 1, 2, 8, 5, 2, 10, 8, 4, 5, 8, -1, -1, -1, 0, 4, 10, 0, 10, 3,
        4, 5, 10, 2, 10, 1, 5, 1, 10, 0, 2, 5, 0, 5, 9, 2, 10, 5, 4, 5, 8,
        10, 8, 5, 9, 4, 5, 2, 10, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, 2,
        5, 11, 3, 5, 2, 3, 4, 5, 3, 8, 4, -1, -1, -1, 5, 11, 2, 5, 2, 4, 4,
        2, 0, -1, -1, -1, -1, -1, -1, 3, 11, 2, 3, 5, 11, 3, 8, 5, 4, 5, 8,
        0, 1, 9, 5, 11, 2, 5, 2, 4, 1, 9, 2, 9, 4, 2, -1, -1, -1, 8, 4, 5,
        8, 5, 3, 3, 5, 1, -1, -1, -1, -1, -1, -1, 0, 4, 5, 1, 0, 5, -1, -1,
        -1, -1, -1, -1, -1, -1, -1, 8, 4, 5, 8, 5, 3, 9, 0, 5, 0, 3, 5, -1,
        -1, -1, 9, 4, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 4,
        10, 7, 4, 9, 10, 9, 11, 10, -1, -1, -1, -1, -1, -1, 0, 8, 3, 4, 9,
        7, 9, 10, 7, 9, 11, 10, -1, -1, -1, 1, 11, 10, 1, 10, 4, 1, 4, 0,
        7, 4, 10, -1, -1, -1, 3, 1, 4, 3, 4, 8, 1, 11, 4, 7, 4, 10, 11, 10,
        4, 4, 10, 7, 9, 10, 4, 9, 2, 10, 9, 1, 2, -1, -1, -1, 9, 7, 4, 9,
        10, 7, 9, 1, 10, 2, 10, 1, 0, 8, 3, 10, 7, 4, 10, 4, 2, 2, 4, 0,
        -1, -1, -1, -1, -1, -1, 10, 7, 4, 10, 4, 2, 8, 3, 4, 3, 2, 4, -1,
        -1, -1, 2, 9, 11, 2, 7, 9, 2, 3, 7, 7, 4, 9, -1, -1, -1, 9, 11, 7,
        9, 7, 4, 11, 2, 7, 8, 7, 0, 2, 0, 7, 3, 7, 11, 3, 11, 2, 7, 4, 11,
        1, 11, 0, 4, 0, 11, 1, 11, 2, 8, 7, 4, -1, -1, -1, -1, -1, -1, -1,
        -1, -1, 4, 9, 1, 4, 1, 7, 7, 1, 3, -1, -1, -1, -1, -1, -1, 4, 9, 1,
        4, 1, 7, 0, 8, 1, 8, 7, 1, -1, -1, -1, 4, 0, 3, 7, 4, 3, -1, -1,
        -1, -1, -1, -1, -1, -1, -1, 4, 8, 7, -1, -1, -1, -1, -1, -1, -1,
        -1, -1, -1, -1, -1, 9, 11, 8, 11, 10, 8, -1, -1, -1, -1, -1, -1,
        -1, -1, -1, 3, 0, 9, 3, 9, 10, 10, 9, 11, -1, -1, -1, -1, -1, -1,
        0, 1, 11, 0, 11, 8, 8, 11, 10, -1, -1, -1, -1, -1, -1, 3, 1, 11,
        10, 3, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 2, 10, 1, 10, 9,
        9, 10, 8, -1, -1, -1, -1, -1, -1, 3, 0, 9, 3, 9, 10, 1, 2, 9, 2,
        10, 9, -1, -1, -1, 0, 2, 10, 8, 0, 10, -1, -1, -1, -1, -1, -1, -1,
        -1, -1, 3, 2, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
        2, 3, 8, 2, 8, 11, 11, 8, 9, -1, -1, -1, -1, -1, -1, 9, 11, 2, 0,
        9, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, 2, 3, 8, 2, 8, 11, 0, 1,
        8, 1, 11, 8, -1, -1, -1, 1, 11, 2, -1, -1, -1, -1, -1, -1, -1, -1,
        -1, -1, -1, -1, 1, 3, 8, 9, 1, 8, -1, -1, -1, -1, -1, -1, -1, -1,
        -1, 0, 9, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 3,
        8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
        -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1];