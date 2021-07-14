{% if document %}
    <ul>
        {% for token in document %}
            <li> {{ token.text }} </li>
        {% endfor %}
    </ul>
{% else %}
        <p>No document available.</p>
{% endif %}