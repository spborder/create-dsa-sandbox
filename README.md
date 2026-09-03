# create-dsa-sandbox

This package enables the creation of local directories containing item data from a Digital Slide Archive (DSA) instance. This can be useful for developing local tools or for running scripts that rely on item data from a DSA.

## Installation

To install this package, you can use pip:

```bash
pip install create-dsa-sandbox
```

## Usage

Once installed, you can use the `create-dsa-sandbox` command to create local directories containing item data from a DSA instance. For example:

```bash
create-dsa-sandbox --dsa-url="https://example.com/dsa" --item-id="" --output-dir="/path/to/output/directory"
```

This command will create a local directory in the specified output directory named `/path/to/output/directory` containing item data from the DSA instance specified in the other arguments.
