import argparse
import sys
import importlib
import tensorflow as tf


def map_dims(dims):
    return list(map(lambda x: None if x=='?' else int(x), dims.split(',')))


def freeze_model(params):
    input = tf.placeholder(tf.float32, map_dims(params.in_dims), name='input')
    module = importlib.import_module(params.module_name)
    class_ = getattr(module, params.class_name)
    net = class_({'data': input})
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        net.load(params.weights, sess)


        output_graph_def = tf.graph_util.convert_variables_to_constants(
            sess,
            tf.get_default_graph().as_graph_def(),
            params.out_names.split(',')
        )
        output_graph_def = tf.graph_util.remove_training_nodes(output_graph_def)

        with tf.gfile.GFile(params.out_file, "wb") as f:
            f.write(output_graph_def.SerializeToString())
        #tf.train.write_graph(output_graph_def, '.', params.out_file, as_text=False)
        print("%d ops in the final graph." % len(output_graph_def.node))

def main():
    parser = argparse.ArgumentParser(description='Autogenerated model freezer')

    parser.add_argument('--module_name', action="store", dest="module_name",
                        help='Model class module', required=True)

    parser.add_argument('--class_name', action="store", dest="class_name",
                        help='Model class name', required=True)

    parser.add_argument('--out_names', action="store", dest="out_names",
                        help='Names of outputs', required=True)

    parser.add_argument('--in_dims', action="store", dest="in_dims",
                        help='Input dimensions list', required=True)

    parser.add_argument('--weights', action="store", dest="weights",
                        help='Weights file', required=True)


    parser.add_argument('--out_file', action="store", dest="out_file",
                        help='Output graph file', required=True)

    params = parser.parse_args(sys.argv[1:])

    freeze_model(params)

if __name__ == "__main__":
    main()

