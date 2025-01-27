#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import xml.etree.ElementTree as ET
import subprocess

VERSION = '0.0.1'

def perror(*args):
  sys.stderr.write(*args)
  sys.stderr.write('\n')

def output2xml(strings):
  # 行単位にパースして辞書形式にする
  dicts = [read_line(line) for line in strings.split('\n') if line != '']

  # 同ファイル名毎にリスト化
  files = {}
  for dic in dicts:
    if dic['file'] not in files:
      files[dic['file']] = []
    files[dic['file']].append(dic)

  # XMLのツリーに変換
  root = ET.Element('checkstyle')
  root.attrib['version'] = '8.0'

  for file in files.keys():
      file_element = ET.SubElement(root, 'file', attrib={'name':file})
      for dic in files[file]:
        file_element.append(line2element(dic))

  return root

def read_line(line):
  result = dict(zip(['severity', 'type', 'source', 'file', 'line', 'column', 'message_type', 'message'], line.split('|')))
  result['severity'] = result['severity'].lower()
  return result


# """
# <error line='15' column='50' severity='info' message='Avoid using braces in interpolation when not needed.' source='unnecessary_brace_in_string_interps'/>
# """
def line2element(dic):
  attributes = {k: v for k, v in dic.items() if k in ['line', 'column', 'severity', 'message', 'source']}
  element = ET.Element('error', attrib=attributes)
  return element

# Help
def show_help():
  perror('Usage: dartcop [options...] <directory or list of files>')
  perror('       dartcop --version')
  perror('')
  perror('dartcop')
  perror('Homepage: https://github.com/kuronekomichael/dartcop')
  perror('Simple `dartanalyzer` wrapper convert to checkstyle format')
  exit(255)

def main(argv):
  if len(argv) == 0:
    return False

  if argv[0] == '-V' or argv[0] == '--version':
    print('dartcop v' + VERSION)
    exit(0)

  if argv[0] == 'help':
    show_help()
    exit(0)

  try:
    subprocess.check_output(['which', 'dartanalyzer'], stderr=subprocess.STDOUT)
  except subprocess.CalledProcessError as cpe:
    perror('ERROR!!')
    perror('dartanalyzer not found. Install Dart SDK and add it to PATH.')
    exit(1)

  if any([v == '--format=human' for v in argv]):
    perror('ERROR!!')
    perror('Cannot set --format=human.')
    exit(1)

  try:
    ret = subprocess.check_output(['dartanalyzer', '--format=machine'] + argv, stderr=subprocess.STDOUT)
  except subprocess.CalledProcessError as cpe:
    ret = cpe.output

  checkstyle = output2xml(ret.decode('utf-8'))

  checkStyleFile = ET.ElementTree(checkstyle)
  checkStyleFile.write('output_checkstyle.xml')

  exit(0)

if __name__ == '__main__':
  main(sys.argv[1:])
