# Installation

## Using pip

With `pip` (or `uv`), you can install Uplink simply by typing:

    $ pip install -U uplink

## Download the Source Code

Uplink's source code is in a [public repository hosted on
GitHub](https://github.com/prkumar/uplink).

As an alternative to installing with `pip`, you could clone the
repository,

    $ git clone https://github.com/prkumar/uplink.git

then, install; e.g., with `setup.py`:

    $ cd uplink
    $ python setup.py install

## Extras

These are optional integrations and features that extend the library's
core functionality and typically require an additional dependency.

When installing Uplink with `pip`, you can specify any of the following
extras, to add their respective dependencies to your installation:

<table>
<thead>
<tr>
<th>Extra</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>aiohttp</code></td>
<td>Enables <code class="interpreted-text"
role="py:class">uplink.AiohttpClient</code>, for <a
href="https://github.com/prkumar/uplink/tree/master/examples/async-requests">sending
non-blocking requests</a> and receiving awaitable responses.</td>
</tr>
<tr>
<td><code>marshmallow</code></td>
<td>Enables <code class="interpreted-text"
role="py:class">uplink.MarshmallowConverter</code>, for <a
href="https://github.com/prkumar/uplink/tree/master/examples/marshmallow">converting
JSON responses directly into Python objects</a> using <code
class="interpreted-text" role="py:class">marshmallow.Schema</code>.</td>
</tr>
<tr>
<td><code>pydantic</code></td>
<td>Enables <code class="interpreted-text"
role="py:class">uplink.PydanticConverter</code>, for converting JSON
responses directly into Python objects using <code
class="interpreted-text" role="py:class">pydantic.BaseModel</code>.</td>
</tr>
<tr>
<td><code>twisted</code></td>
<td>Enables <code class="interpreted-text"
role="py:class">uplink.TwistedClient</code>, for <a
href="https://github.com/prkumar/uplink/tree/master/examples/async-requests">sending
non-blocking requests</a> and receiving <code class="interpreted-text"
role="py:class">~twisted.internet.defer.Deferred</code> responses.</td>
</tr>
</tbody>
</table>

To download all available features, run

    $ pip install -U uplink[aiohttp, marshmallow, pydantic, twisted]
