from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from django.http import HttpResponseRedirect
import markdown2
import random

from . import util

class SearchForm(forms.Form):
    q = forms.CharField(label="", widget=forms.TextInput(attrs={
        "placeholder": "Search Encyclopedia...",
        "class": "form-control"
    }))

class CreateForm(forms.Form):
    title = forms.CharField(label="Title", max_length=200,
                            widget=forms.TextInput(attrs={
                                "autocomplete":"off",
                                "class": "form-control",
                                }))
    content = forms.CharField(label="Content (Markdown)", widget=forms.Textarea(attrs={"class": "form-control","rows":10}))

class EditForm(forms.Form):
    content = forms.CharField(label="Content (Markdown)", widget=forms.Textarea(attrs={"class": "form-control","rows":10}))


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "search_form": SearchForm(),
    })

def entry_page(request, title):
    """
    Converts Markdown -> HTML
    """
    entry_md = util.get_entry(title)
    search_form = SearchForm()

    if entry_md is None:
        return render(request, "encyclopedia/error.html", {
            "message": f"The page '{title}' was not found.",
            "search_form": search_form
        })
    # convert Markdown to HTML
    entry_html = markdown2.markdown(entry_md)
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": entry_html,
        "search_form": search_form
    })
    
    
def search(request):
    """
    If exact match -> redirect to that page.
    Otherwise -> show search results
    """
    if request.method != "GET":
        return redirect(reverse("encyclopedia:index"))

    form = SearchForm(request.GET)
    if not form.is_valid():
        return redirect(reverse("encyclopedia:index"))

    query = form.cleaned_data["q"].strip()
    if not query:
        return redirect(reverse("encyclopedia:index"))

    entries = util.list_entries()
    for e in entries:
        if e.lower() == query.lower():
            return redirect(reverse("encyclopedia:entry", kwargs={"title": e}))

    results = [e for e in entries if query.lower() in e.lower()]

    return render(request, "encyclopedia/search.html", {
        "query": query,
        "results": results,
        "search_form": form
    })
    
    
def create_page(request):
    """
    GET -> show empty create form
    POST -> try to create new page; if title already exists -> error
    """
    search_form = SearchForm()
    if request.method == "POST":
        form = CreateForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"].strip()
            content = form.cleaned_data["content"]

            entries = util.list_entries()
            for e in entries:
                if e.lower() == title.lower():
                    return render(request, "encyclopedia/error.html", {
                        "message": f"A page with the title '{title}' already exists.",
                        "search_form": search_form
                    })
            util.save_entry(title, content)
            return redirect(reverse("encyclopedia:entry", kwargs={"title": title}))
    else:
        form = CreateForm()

    return render(request, "encyclopedia/create.html", {
        "form": form,
        "form_title": "Create New Page",
        "submit_label": "Save",
        "search_form": search_form
    })


def edit_page(request, title):
    """
    Display the edit form with the current Markdown content.
    """
    # Get current entry content
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": "Page not found."
        })

    # Pre-fill the form with existing content
    form = EditForm(initial={"content": content})
    search_form = SearchForm()

    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "form": form,
        "search_form": search_form
    })



def save_edit(request, title):
    """
    Handle POST from edit page to save new Markdown and redirect to entry page.
    """
    if request.method != "POST":
        return redirect(reverse("encyclopedia:edit", kwargs={"title": title}))

    form = EditForm(request.POST)
    search_form = SearchForm()
    if not form.is_valid():
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "form": form,
            "search_form": search_form
        })

    content = form.cleaned_data["content"]
    # Overwrite existing entry
    util.save_entry(title, content)
    return redirect(reverse("encyclopedia:entry", kwargs={"title": title}))


def random_page(request):
    entries = util.list_entries()
    if not entries:
        return render(request, "encyclopedia/error.html", {
            "message": "No encyclopedia entries available.",
            "search_form": SearchForm()
        })
    choice = random.choice(entries)
    return redirect(reverse("encyclopedia:entry", kwargs={"title": choice}))
