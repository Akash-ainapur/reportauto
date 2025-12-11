    def _configure_page_numbering(self):
        """
        Configure professional page numbering:
        - Roman numerals (i, ii, iii) for preliminary pages (Abstract, Acknowledgement, TOC)
        - Arabic numerals (1, 2, 3...) starting from Introduction with restart
        """
        if not self.master_doc:
            return
        
        print("  📊 Configuring page numbering...")
        
        for section_idx, section in enumerate(self.master_doc.sections):
            sectPr = section._sectPr
            
            # Remove existing page number settings
            pgNumType_list = sectPr.findall(qn('w:pgNumType'))
            for pgNumType in pgNumType_list:
                sectPr.remove(pgNumType)
            
            # Create new pgNumType element
            pgNumType = OxmlElement('w:pgNumType')
            
            if section_idx <= 2:
                # Front Page, Certificate, Declaration: Continue (no special formatting)
                # These have no footer anyway due to isolation
                print(f"     Section {section_idx}: Default numbering (hidden)")
                pass
                
            elif 3 <= section_idx <= 5:
                # Abstract (3), Acknowledgement (4), TOC (5): Roman numerals
                pgNumType.set(qn('w:fmt'), 'lowerRoman')  # i, ii, iii
                if section_idx == 3:
                    # Start Roman numbering at i for Abstract
                    pgNumType.set(qn('w:start'), '1')
                    print(f"     Section {section_idx} (Abstract): Roman numerals starting at i")
                else:
                    print(f"     Section {section_idx}: Roman numerals (continue)")
                sectPr.append(pgNumType)
                
            elif section_idx == 6:
                # Introduction: RESTART with Arabic numerals at 1
                pgNumType.set(qn('w:fmt'), 'decimal')  # 1, 2, 3
                pgNumType.set(qn('w:start'), '1')  # RESTART at 1
                sectPr.append(pgNumType)
                print(f"     Section {section_idx} (Introduction): Arabic numerals RESTART at 1")
                
            else:
                # All subsequent chapters: Continue with Arabic numerals
                pgNumType.set(qn('w:fmt'), 'decimal')
                sectPr.append(pgNumType)
                print(f"     Section {section_idx}: Arabic numerals (continue)")
    
    def _generate_table_of_contents(self):
        """
        Generate Table of Contents at section 5 (after Acknowledgement).
        This is done AFTER all content is built for accurate page numbers.
        """
        if not self.master_doc:
            return
        
        print("  📑 Generating Table of Contents...")
        
        # Get section 5 (TOC placeholder)
        if len(self.master_doc.sections) < 6:
            print("     ⚠️  Not enough sections for TOC")
            return
        
        toc_section = self.master_doc.sections[5]
        
        # Find the placeholder paragraph in TOC section
        # We'll replace the placeholder with actual TOC field
        paragraphs_in_section = []
        current_section = 0
        
        for para in self.master_doc.paragraphs:
            # Determine which section this paragraph belongs to
            para_section = para._element.getparent()
            while para_section is not None:
                if para_section.tag == qn('w:body'):
                    break
                para_section = para_section.getparent()
            
            # Find TOC placeholder text
            if '[Table of Contents will be auto-generated here]' in para.text:
                # Clear placeholder
                para.clear()
                
                # Insert TOC field
                run = para.add_run()
                
                # TOC field structure
                fldChar1 = OxmlElement('w:fldChar')
                fldChar1.set(qn('w:fldCharType'), 'begin')
                
                instrText = OxmlElement('w:instrText')
                instrText.set(qn('xml:space'), 'preserve')
                # TOC field with switches:
                # \\o "1-3" = Outline levels 1-3 (Heading 1, 2, 3)
                # \\h = Hyperlinks
                # \\z = Hide page numbers in web view
                # \\u = Use outline levels
                instrText.text = 'TOC \\o "1-3" \\h \\z \\u'
                
                fldChar2 = OxmlElement('w:fldChar')
                fldChar2.set(qn('w:fldCharType'), 'separate')
                
                # Placeholder text (will be replaced when user updates field in Word)
                run_text = para.add_run("Right-click and select 'Update Field'")
                run_text.font.italic = True
                run_text.font.size = Pt(11)
                
                fldChar3 = OxmlElement('w:fldChar')
                fldChar3.set(qn('w:fldCharType'), 'end')
                
                # Append all field elements
                run._element.append(fldChar1)
                run._element.append(instrText)
                run._element.append(fldChar2)
                para._element.append(run_text._element)
                run._element.append(fldChar3)
                
                print("     ✅ TOC field inserted successfully")
                break
