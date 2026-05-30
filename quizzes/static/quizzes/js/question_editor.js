function questionEditor() {
  return {
    preview: {
      text: '',
      questionType: 'single',
      points: 1,
      variants: []
    },
    _sortable: null,

    get questionTypeLabel() {
      var labels = {
        'single': 'Один правильный ответ',
        'multiple': 'Несколько правильных ответов',
        'text': 'Текстовый ответ',
        'matching': 'Сопоставление'
      };
      return labels[this.preview.questionType] || 'Один правильный ответ';
    },

    hasDuplicateTexts: false,
    hasMinVariants: true,
    hasCorrectAnswer: true,
    autoAddEnabled: true,

    init() {
      this.syncPreview();
      this.$nextTick(function() {
        this.bindEvents();
        this.initSortable();
        this.autoResizeAll();
        this.ensureMinForms();
        this.toggleEmptyState();
        this.checkMinVariants();
        this.validateDuplicates();
      }.bind(this));
    },

    _variantNotFilled(t, d) {
      if (!t || (d && d.checked)) return false;
      return t.value.trim() === '';
    },

    ensureMinForms() {
      var totalFormsEl = document.getElementById('id_answer_variants-TOTAL_FORMS');
      var total = totalFormsEl ? parseInt(totalFormsEl.value) : 0;
      var hasEmpty = false;
      for (var i = 0; i < total; i++) {
        var t = document.getElementById('id_answer_variants-' + i + '-text');
        var d = document.getElementById('id_answer_variants-' + i + '-DELETE');
        if (this._variantNotFilled(t, d)) {
          hasEmpty = true;
          break;
        }
      }
      if (!hasEmpty) {
        this.addVariant();
      }
      total = totalFormsEl ? parseInt(totalFormsEl.value) : 0;
      while (total < 2) {
        this.addVariant();
        total = totalFormsEl ? parseInt(totalFormsEl.value) : 0;
      }
    },

    toggleEmptyState() {
      var total = parseInt(document.getElementById('id_answer_variants-TOTAL_FORMS')?.value || 0);
      for (var i = 0; i < total; i++) {
        var t = document.getElementById('id_answer_variants-' + i + '-text');
        var d = document.getElementById('id_answer_variants-' + i + '-DELETE');
        var item = t?.closest('.variant-item');
        if (item) {
          item.dataset.empty = this._variantNotFilled(t, d) ? 'true' : 'false';
        }
      }
    },

    checkMinVariants() {
      var count = this.preview.variants.length;
      this.hasMinVariants = count >= 2;
      this.hasCorrectAnswer = true;
    },

    autoAddVariant() {
      if (!this.autoAddEnabled) return;
      var totalFormsEl = document.getElementById('id_answer_variants-TOTAL_FORMS');
      if (totalFormsEl && parseInt(totalFormsEl.value) >= 100) return;
      var total = parseInt(document.getElementById('id_answer_variants-TOTAL_FORMS')?.value || 0);
      var allFilled = true;
      for (var i = 0; i < total; i++) {
        var t = document.getElementById('id_answer_variants-' + i + '-text');
        var d = document.getElementById('id_answer_variants-' + i + '-DELETE');
        if (this._variantNotFilled(t, d)) {
          allFilled = false;
          break;
        }
      }
      if (allFilled) {
        this.addVariant();
      }
    },

    validateDuplicates() {
      var seen = {};
      var dups = {};
      var total = parseInt(document.getElementById('id_answer_variants-TOTAL_FORMS')?.value || 0);
      for (var i = 0; i < total; i++) {
        var t = document.getElementById('id_answer_variants-' + i + '-text');
        var d = document.getElementById('id_answer_variants-' + i + '-DELETE');
        if (t && (!d || !d.checked) && t.value.trim() !== '') {
          var key = t.value.trim().toLowerCase();
          if (seen[key] !== undefined) {
            dups[seen[key]] = true;
            dups[i] = true;
          } else {
            seen[key] = i;
          }
        }
      }
      this.hasDuplicateTexts = Object.keys(dups).length > 0;
      for (var j = 0; j < total; j++) {
        var el = document.getElementById('id_answer_variants-' + j + '-text');
        if (el) {
          if (dups[j]) {
            el.classList.add('border-red-500', 'focus:border-red-500');
            el.classList.remove('focus:border-cyan-500');
          } else {
            el.classList.remove('border-red-500', 'focus:border-red-500');
            el.classList.add('focus:border-cyan-500');
          }
        }
      }
    },

    syncPreview() {
      var textEl = document.getElementById('id_text');
      var typeEl = document.getElementById('id_question_type');
      var pointsEl = document.getElementById('id_points');
      var totalFormsEl = document.getElementById('id_answer_variants-TOTAL_FORMS');

      if (textEl) this.preview.text = textEl.value;
      if (typeEl) this.preview.questionType = typeEl.value;
      if (pointsEl) this.preview.points = parseInt(pointsEl.value) || 1;

      var variants = [];
      var total = totalFormsEl ? parseInt(totalFormsEl.value) : 0;

      for (var i = 0; i < total; i++) {
        var t = document.getElementById('id_answer_variants-' + i + '-text');
        var d = document.getElementById('id_answer_variants-' + i + '-DELETE');

        if (t && (!d || !d.checked) && t.value.trim() !== '') {
          variants.push({ text: t.value, matchText: '', isCorrect: false });
        }
      }
      this.preview.variants = variants;
      this.checkMinVariants();
    },

    bindEvents() {
      var form = document.getElementById('questionForm');
      var container = document.getElementById('variants-container');
      if (!form) return;
      var self = this;

      form.addEventListener('submit', function(e) {
        self.syncPreview();
        self.validateDuplicates();
        self.checkMinVariants();
        console.log('[Submit] hasMinVariants:', self.hasMinVariants, 'hasCorrectAnswer:', self.hasCorrectAnswer, 'variants:', JSON.stringify(self.preview.variants));
        if (self.hasDuplicateTexts || !self.hasMinVariants || !self.hasCorrectAnswer) {
          e.preventDefault();
        }
      });

      form.addEventListener('input', function(e) {
        self.syncPreview();
        self.toggleEmptyState();
        self.autoAddVariant();
        self.validateDuplicates();
        if (e.target.matches('.variant-textarea')) {
          self.autoResizeTextarea(e.target);
        }
      });
      form.addEventListener('change', function(e) {
        self.syncPreview();
        self.toggleEmptyState();
        self.checkMinVariants();
        self.validateDuplicates();
      });

      document.getElementById('id_question_type')?.addEventListener('change', function() {
        self.syncPreview();
        self.checkMinVariants();
      });

      if (container) {
        container.addEventListener('click', function(e) {
          var btn = e.target.closest('[data-remove-variant]');
          if (btn) self.removeVariant(btn);
        });
      }
    },

    reindexVariants() {
      var items = document.querySelectorAll('#variants-container .variant-item');

      items.forEach(function(item, index) {
        item.querySelectorAll('[name], [id]').forEach(function(el) {
          var name = el.getAttribute('name');
          var id = el.getAttribute('id');
          if (name) el.setAttribute('name', name.replace(/answer_variants-\d+/g, 'answer_variants-' + index));
          if (id) el.setAttribute('id', id.replace(/answer_variants-\d+/g, 'answer_variants-' + index));
        });
        item.querySelectorAll('[for]').forEach(function(el) {
          var htmlFor = el.getAttribute('for');
          if (htmlFor) el.setAttribute('for', htmlFor.replace(/answer_variants-\d+/g, 'answer_variants-' + index));
        });
        item.dataset.index = index;
        var orderInput = item.querySelector('[name$="-order"]');
        if (orderInput) orderInput.value = index;
      });

      var totalForms = document.getElementById('id_answer_variants-TOTAL_FORMS');
      if (totalForms) totalForms.value = items.length;
      this.toggleEmptyState();
      this.ensureMinForms();
      this.autoAddVariant();
      this.validateDuplicates();
    },

    addVariant() {
      var totalFormsEl = document.getElementById('id_answer_variants-TOTAL_FORMS');
      var currentTotal = totalFormsEl ? parseInt(totalFormsEl.value) : 0;
      if (currentTotal >= 100) return;

      var container = document.getElementById('variants-container');
      totalFormsEl = document.getElementById('id_answer_variants-TOTAL_FORMS');
      var index = totalFormsEl ? parseInt(totalFormsEl.value) : 0;
      var stubText = {
        single: '✓ будет отмечаться правильный ответ',
        multiple: '☑ будут отмечаться правильные ответы',
        text: '✎ будет вводиться текстовый ответ',
        matching: '⇄ будет текст сопоставления'
      }[this.preview.questionType] || '';

      var div = document.createElement('div');
      div.className = 'variant-item flex items-start gap-3 rounded-xl border border-white/10 bg-slate-800/40 p-3 transition hover:border-white/20';
      div.dataset.index = index;
      div.dataset.empty = 'true';
      div.innerHTML =
        '<div class="drag-handle mt-2.5 flex-shrink-0 text-slate-500">' +
          '<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M5 2a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm4 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zM5 6a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm4 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zM5 10a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm4 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"/></svg>' +
        '</div>' +
        '<div class="flex-grow min-w-0">' +
          '<textarea name="answer_variants-' + index + '-text" id="id_answer_variants-' + index + '-text" maxlength="255" placeholder="Вариант ответа" rows="1"' +
            ' class="variant-textarea w-full resize-none overflow-hidden rounded-lg border border-white/10 bg-slate-700/40 px-3 py-2 text-white placeholder-slate-400 transition focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500"></textarea>' +
          '<div class="mt-2 rounded-lg border border-dashed border-white/5 bg-slate-800/20 px-3 py-2 text-xs text-slate-500">' + stubText + '</div>' +
        '</div>' +
        '<input type="hidden" name="answer_variants-' + index + '-order" id="id_answer_variants-' + index + '-order" value="' + index + '">' +
        '<button type="button" data-remove-variant' +
          ' class="mt-2 flex-shrink-0 rounded-lg p-1 text-slate-500 transition hover:bg-red-500/20 hover:text-red-400" title="Удалить вариант">' +
          '<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/></svg>' +
        '</button>';

      container.appendChild(div);
      if (totalFormsEl) totalFormsEl.value = index + 1;

      container.querySelectorAll('.variant-item:last-child .variant-textarea').forEach(function(el) {
        self.autoResizeTextarea(el);
      });
      this.initSortable();
      this.syncPreview();
      this.validateDuplicates();
    },

    removeVariant(button) {
      var item = button.closest('.variant-item');
      if (!item) return;

      var deleteCheckbox = item.querySelector('[name$="-DELETE"]');

      if (deleteCheckbox) {
        deleteCheckbox.checked = true;
        item.classList.add('variant-item-deleted');
        item.style.display = 'none';
      } else {
        item.remove();
        this.reindexVariants();
      }

      this.syncPreview();
      this.toggleEmptyState();
      this.ensureMinForms();
      this.autoAddVariant();
      this.validateDuplicates();
    },

    autoResizeTextarea(el) {
      el.style.height = '';
      el.style.height = el.scrollHeight + 'px';
    },

    autoResizeAll() {
      document.querySelectorAll('.variant-textarea').forEach(function(el) {
        el.style.height = '';
        el.style.height = el.scrollHeight + 'px';
      });
    },

    initSortable() {
      var container = document.getElementById('variants-container');
      if (!container) return;

      if (this._sortable) {
        this._sortable.destroy();
      }

      var self = this;
      this._sortable = new Sortable(container, {
        animation: 200,
        easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
        handle: '.drag-handle',
        filter: '[data-empty="true"]',
        preventOnFilter: false,
        ghostClass: 'sortable-ghost',
        chosenClass: 'sortable-chosen',
        onEnd: function() {
          self.reindexVariants();
          self.syncPreview();
          self.toggleEmptyState();
          self.autoAddVariant();
          self.validateDuplicates();
        }
      });
    }
  };
}
