def visualizeTree(tree_root):
    '''
    This function visualizes the decision tree given a root. Written for C S 363D Assignment 1.
    
    Dependencies: python-igraph, plotly
    Created: Xiya Yang, 10 Feb 2018
    Contains code adapted from https://plot.ly/python/tree-plots/
    '''
    class orderableNode():
        _id = 0

        def __init__(self, level, node):
            self.level = level
            self.node = node
            self._id = orderableNode._id
            orderableNode._id += 1

        def __lt__(self, other):
            return self.level < other.level
        def __gt__(self, other):
            return self.level > other.level
        def __eq__(self, other):
            return self.level == other.level

    from igraph import Graph

    import plotly.plotly as py
    import plotly.graph_objs as go

    vertices = []
    edges = []
    annotations = []

    orderableNode._id = 0

    def build_vertices_and_edges(tree_root):
        import heapq
        pq = []
        _id = 0

        def add_child(o_node, child):
            heapq.heappush(pq, child)
            edges.append((o_node._id, child._id))

        def add_edge(o_node):
            if o_node.node.left_child:
                child = orderableNode(o_node.level+1, o_node.node.left_child)
                add_child(o_node, child)
            if o_node.node.right_child:
                child = orderableNode(o_node.level+1, o_node.node.right_child)
                add_child(o_node, child)

        def add_id_annotation(o_node, is_leaf=False):
            vertices.append(o_node._id)
            if is_leaf:
                annotation = "%d" % o_node.node.prediction
            else:
                annotation = "Ft[%d]<%.2f" % (o_node.node.feature_idx, o_node.node.thresh_val)
            annotations.append(annotation)

        heapq.heappush(pq, orderableNode(1, tree_root))
        while len(pq) > 0:
            orderable_node = heapq.heappop(pq)
            level = orderable_node.level

            if not orderable_node.node.is_leaf:
                add_id_annotation(orderable_node)
                add_edge(orderable_node)
            else:
                add_id_annotation(orderable_node, is_leaf=True)

    build_vertices_and_edges(tree_root)
    
    G = Graph()
    G.add_vertices(vertices)
    G.add_edges(edges)

    lay = G.layout('rt',mode='all', root=[0])
    position = {k: lay[k] for k in vertices}
    Y = [lay[k][1] for k in vertices]
    M = max(Y)
    L = len(position)
    Xn = [position[k][0] for k in range(L)]
    Yn = [2*M-position[k][1] for k in range(L)]
    Xe = []
    Ye = []
    for edge in edges:
        Xe+=[position[edge[0]][0],position[edge[1]][0], None]
        Ye+=[2*M-position[edge[0]][1],2*M-position[edge[1]][1], None] 

    lines = go.Scatter(x=Xe,
                   y=Ye,
                   mode='lines',
                   line=dict(color='rgb(210,210,210)', width=1),
                   hoverinfo='none'
                   )
    dots = go.Scatter(x=Xn,
                      y=Yn,
                      mode='markers',
                      name='',
                      marker=dict(symbol='marker',
                                    size=1, 
                                    color='#6175c1',    #'#DB4551', 
                                    line=dict(color='rgb(50,50,50)', width=1)
                                    ),
                      text=annotations,
                      hoverinfo='text',
                      opacity=0.8
                      )
    vertex_to_i = {vertices[i]: i for i in range(len(vertices))}

    def make_annotations(pos, text, font_size=14, font_color='#fff'):
        if len(text)!=L:
            raise ValueError('The lists pos and text must have the same len')
        labels = go.Annotations()
        for k in pos:
            labels.append(
                go.Annotation(
                    text=annotations[vertex_to_i[k]],
                    x=pos[k][0], y=2*M-position[k][1],
                    xref='x1', yref='y1',
                    font=dict(color=font_color, size=font_size),
                    showarrow=False,
                    bgcolor='#6175c1',
                    bordercolor='#c7c7c7',
                    borderwidth=1,
                    borderpad=2,
                ),
            )
        return labels
    
    axis = dict(showline=False, # hide axis line, grid, ticklabels and  title
                zeroline=False,
                showgrid=False,
                showticklabels=False,
                )

    layout = dict(title= 'Decision Tree Visualization',  
                  annotations=make_annotations(position, annotations),
                  font=dict(size=10),
                  showlegend=False,
                  xaxis=go.XAxis(axis),
                  yaxis=go.YAxis(axis),          
                  margin=dict(l=40, r=40, b=85, t=100),
                  hovermode='closest',
                  plot_bgcolor='#fff'
                  )

    data=go.Data([lines, dots])
    fig=dict(data=data, layout=layout)
    fig['layout'].update(annotations=make_annotations(position, annotations))
    return py.iplot(fig)